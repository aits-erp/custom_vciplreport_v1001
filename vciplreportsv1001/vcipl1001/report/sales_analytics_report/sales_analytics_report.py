# Copyright (c) 2013, Frappe Technologies Pvt. Ltd.
# License: MIT

import frappe
from frappe import _, scrub
from frappe.query_builder import DocType
from frappe.query_builder.functions import IfNull
from frappe.utils import add_days, add_to_date, flt, getdate
from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
    return Analytics(filters).run()


class Analytics:
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.date_field = (
            "transaction_date"
            if self.filters.doc_type in ["Sales Order", "Purchase Order"]
            else "posting_date"
        )
        self.months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        self.get_period_date_ranges()

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------

    def run(self):
        self.get_columns()
        self.get_data()
        self.get_chart_data()
        return self.columns, self.data, None, self.chart, None, 0

    # ------------------------------------------------------------------
    # COLUMNS
    # ------------------------------------------------------------------

    def get_columns(self):
        self.columns = [{
            "label": _(self.filters.tree_type),
            "fieldname": "entity",
            "fieldtype": "Data",   # 👈 Data, not Link (important)
            "width": 220,
        }]

        for d in self.periodic_daterange:
            p = self.get_period(d)
            self.columns.append({
                "label": _(p),
                "fieldname": scrub(p),
                "fieldtype": "Float",
                "width": 120,
            })

        self.columns.append({
            "label": _("Total"),
            "fieldname": "total",
            "fieldtype": "Float",
            "width": 120,
        })

    # ------------------------------------------------------------------
    # DATA ROUTER
    # ------------------------------------------------------------------

    def get_data(self):
        if self.filters.tree_type == "Customer":
            self.data = []
            return

        if self.filters.tree_type == "Supplier":
            self.get_supplier_data()
            self.get_rows()

        elif self.filters.tree_type in ["Customer Group", "Supplier Group", "Territory"]:
            self.get_group_data()
            self.get_rows_by_group()

        elif self.filters.tree_type == "Item":
            self.get_item_data()
            self.get_rows()

        elif self.filters.tree_type == "Item Group":
            self.get_item_group_data()
            self.get_rows_by_group()

        elif self.filters.tree_type == "Project":
            self.get_project_data()
            self.get_rows()

        elif self.filters.tree_type == "Order Type":
            self.get_order_type_data()
            self.get_rows_by_group()

        else:
            self.data = []

    # ------------------------------------------------------------------
    # CUSTOMER GROUP DATA (CUSTOMER NAME ONLY)
    # ------------------------------------------------------------------

    def get_group_data(self):
        value_field = "base_net_total" if self.filters.value_quantity == "Value" else "total_qty"

        doctype = DocType(self.filters.doc_type)
        customer = DocType("Customer")

        entries = (
            frappe.qb.from_(doctype)
            .join(customer)
            .on(doctype.customer == customer.name)
            .select(
                customer.customer_group.as_("entity_group"),
                customer.custom_sub_group.as_("custom_sub_group"),
                customer.name.as_("customer"),
                customer.customer_name.as_("customer_name"),
                doctype[value_field].as_("value_field"),
                doctype[self.date_field],
            )
            .where(
                (doctype.docstatus == 1)
                & (doctype.company == self.filters.company)
                & (doctype[self.date_field].between(self.filters.from_date, self.filters.to_date))
            )
        ).run(as_dict=True)

        self.entries = []
        self.sub_group_map = {}
        self.customer_map = {}
        self.customer_labels = {}

        for e in entries:
            grp = e.entity_group
            sg = e.custom_sub_group
            cust = e.customer
            cname = e.customer_name

            node = f"{grp}::SUB::{sg}" if sg else grp
            if sg:
                self.sub_group_map.setdefault(grp, set()).add(sg)

            self.entries.append({
                "entity": node,
                "customer": cust,
                self.date_field: e[self.date_field],
                "value_field": e.value_field,
            })

            if cust:
                self.customer_map.setdefault(node, set()).add(cust)
                # 🔥 KEY FIX: ONLY CUSTOMER NAME
                self.customer_labels[cust] = cname or cust

        self.get_groups()

    # ------------------------------------------------------------------
    # ROW BUILDING
    # ------------------------------------------------------------------

    def get_rows_by_group(self):
        self.build_periodic_data()
        out = []

        for g in reversed(self.group_entries):
            base_indent = self.depth_map.get(g.name, 0)
            block = []

            row = {"entity": g.name, "indent": base_indent}
            total = 0

            for d in self.periodic_daterange:
                p = scrub(self.get_period(d))
                val = flt(self.entity_periodic_data.get(g.name, {}).get(p))
                row[p] = val
                total += val

            row["total"] = total
            block.append(row)

            # Subgroups
            for sg in sorted(self.sub_group_map.get(g.name, [])):
                node = f"{g.name}::SUB::{sg}"
                sg_row = {"entity": sg, "indent": base_indent + 1}
                total_sg = 0

                for d in self.periodic_daterange:
                    p = scrub(self.get_period(d))
                    v = flt(self.entity_periodic_data.get(node, {}).get(p))
                    sg_row[p] = v
                    total_sg += v

                sg_row["total"] = total_sg
                block.append(sg_row)

                # Customers (NAME ONLY)
                for cust in sorted(self.customer_map.get(node, [])):
                    cname = self.customer_labels.get(cust)
                    c_row = {"entity": cname, "indent": base_indent + 2}
                    total_c = 0

                    for d in self.periodic_daterange:
                        p = scrub(self.get_period(d))
                        v = flt(self.entity_periodic_data.get(cust, {}).get(p))
                        c_row[p] = v
                        total_c += v

                    c_row["total"] = total_c
                    block.append(c_row)

            out = block + out

        self.data = out

    # ------------------------------------------------------------------
    # PERIODIC HELPERS
    # ------------------------------------------------------------------

    def build_periodic_data(self):
        self.entity_periodic_data = {}

        for d in self.entries:
            entity = d.get("entity")
            date = d.get(self.date_field)
            if not entity or not date:
                continue

            p = scrub(self.get_period(date))
            self.entity_periodic_data.setdefault(entity, {}).setdefault(p, 0)
            self.entity_periodic_data[entity][p] += flt(d.get("value_field"))

            cust = d.get("customer")
            if cust:
                self.entity_periodic_data.setdefault(cust, {}).setdefault(p, 0)
                self.entity_periodic_data[cust][p] += flt(d.get("value_field"))

    # ------------------------------------------------------------------
    # PERIOD
    # ------------------------------------------------------------------

    def get_period(self, date):
        if self.filters.range == "Monthly":
            return f"{self.months[date.month - 1]} {date.year}"
        if self.filters.range == "Quarterly":
            return f"Q{((date.month - 1)//3) + 1} {date.year}"
        return str(get_fiscal_year(date)[0])

    def get_period_date_ranges(self):
        from_date = getdate(self.filters.from_date)
        to_date = getdate(self.filters.to_date)

        step = 1 if self.filters.range == "Monthly" else 3 if self.filters.range == "Quarterly" else 12
        self.periodic_daterange = []

        while from_date <= to_date:
            end = add_to_date(from_date, months=step, days=-1)
            self.periodic_daterange.append(min(end, to_date))
            from_date = add_days(end, 1)

    # ------------------------------------------------------------------
    # GROUP TREE
    # ------------------------------------------------------------------

    def get_groups(self):
        parent_field = "parent_customer_group"
        self.depth_map = {}

        self.group_entries = frappe.db.sql(
            f"""SELECT name, {parent_field} AS parent, lft, rgt
                FROM `tabCustomer Group`
                ORDER BY lft""",
            as_dict=True,
        )

        for g in self.group_entries:
            self.depth_map[g.name] = self.depth_map.get(g.parent, -1) + 1

    # ------------------------------------------------------------------
    # CHART
    # ------------------------------------------------------------------

    def get_chart_data(self):
        self.chart = {
            "type": "line",
            "data": {
                "labels": [self.get_period(d) for d in self.periodic_daterange],
                "datasets": [],
            },
        }
