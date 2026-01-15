# Copyright (c) 2013, Frappe Technologies Pvt. Ltd.
# License: MIT

import frappe
from frappe import _, scrub
from frappe.query_builder import DocType
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

    # =====================================================
    # RUN
    # =====================================================

    def run(self):
        self.get_columns()
        self.get_data()
        self.get_chart_data()
        return self.columns, self.data, None, self.chart, None, 0

    # =====================================================
    # COLUMNS
    # =====================================================

    def get_columns(self):
        self.columns = [{
            "label": _(self.filters.tree_type),
            "fieldname": "entity",
            "fieldtype": "Data",
            "width": 260,
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

    # =====================================================
    # DATA ROUTER
    # =====================================================

    def get_data(self):
        if self.filters.tree_type == "Customer Group":
            self.get_customer_group_data()
            self.build_rows()
        elif self.filters.tree_type == "Item Group":
            self.get_item_group_data()
            self.build_rows()
        else:
            self.data = []

    # =====================================================
    # CUSTOMER GROUP DATA (SAFE)
    # =====================================================

    def get_customer_group_data(self):
        doctype = DocType(self.filters.doc_type)
        customer = DocType("Customer")

        has_sub = frappe.db.has_column("Customer", "custom_sub_group")

        fields = [
            customer.customer_group.as_("group"),
            customer.name.as_("customer"),
            customer.customer_name.as_("customer_name"),
            doctype.base_net_total.as_("value_field"),
            doctype[self.date_field],
        ]

        if has_sub:
            fields.insert(1, customer.custom_sub_group.as_("sub_group"))

        rows = (
            frappe.qb.from_(doctype)
            .join(customer).on(doctype.customer == customer.name)
            .select(*fields)
            .where(
                (doctype.docstatus == 1)
                & (doctype.company == self.filters.company)
                & (doctype[self.date_field].between(self.filters.from_date, self.filters.to_date))
            )
        ).run(as_dict=True)

        self.entries = []
        self.labels = {}

        for r in rows:
            node = r.group
            if has_sub and r.get("sub_group"):
                node = f"{node}::SUB::{r.sub_group}"

            self.entries.append({
                "entity": node,
                "leaf": r.customer,
                "date": r[self.date_field],
                "value": r.value_field,
            })

            # NAME ONLY
            self.labels[r.customer] = r.customer_name

    # =====================================================
    # ITEM GROUP DATA (SAFE + CUSTOM FIELDS)
    # =====================================================

    def get_item_group_data(self):
        item = DocType("Item")
        item_row = DocType(f"{self.filters.doc_type} Item")
        doc = DocType(self.filters.doc_type)

        has_main = frappe.db.has_column("Item", "custom_main_group")
        has_sub = frappe.db.has_column("Item", "custom_sub_group")
        has_sub1 = frappe.db.has_column("Item", "custom_sub_group1")

        fields = [
            item.item_group.as_("group"),
            item.name.as_("item"),
            item.item_name.as_("item_name"),
            item_row.base_net_amount.as_("value_field"),
            doc.posting_date,
        ]

        if has_main:
            fields.insert(1, item.custom_main_group.as_("main_group"))
        if has_sub:
            fields.insert(2, item.custom_sub_group.as_("sub_group"))
        if has_sub1:
            fields.insert(3, item.custom_sub_group1.as_("sub_group1"))

        rows = (
            frappe.qb.from_(item_row)
            .join(doc).on(item_row.parent == doc.name)
            .join(item).on(item_row.item_code == item.name)
            .select(*fields)
            .where(
                (doc.docstatus == 1)
                & (doc.company == self.filters.company)
                & (doc.posting_date.between(self.filters.from_date, self.filters.to_date))
            )
        ).run(as_dict=True)

        self.entries = []
        self.labels = {}

        for r in rows:
            node = r.group

            if has_main and r.get("main_group"):
                node = f"{node}::MAIN::{r.main_group}"
            if has_sub and r.get("sub_group"):
                node = f"{node}::SUB::{r.sub_group}"
            if has_sub1 and r.get("sub_group1"):
                node = f"{node}::SUB1::{r.sub_group1}"

            self.entries.append({
                "entity": node,
                "leaf": r.item,
                "date": r.posting_date,
                "value": r.value_field,
            })

            # ITEM NAME ONLY
            self.labels[r.item] = r.item_name

    # =====================================================
    # BUILD ROWS (COMMON)
    # =====================================================

    def build_rows(self):
        self.build_periodic_data()
        out = []

        for entity, pdata in self.periodic.items():
            row = {"entity": entity}
            total = 0

            for d in self.periodic_daterange:
                p = scrub(self.get_period(d))
                val = flt(pdata.get(p))
                row[p] = val
                total += val

            row["total"] = total
            out.append(row)

        self.data = out

    def build_periodic_data(self):
        self.periodic = {}

        for e in self.entries:
            p = scrub(self.get_period(e["date"]))

            self.periodic.setdefault(e["entity"], {}).setdefault(p, 0)
            self.periodic[e["entity"]][p] += flt(e["value"])

            leaf = e.get("leaf")
            if leaf:
                self.periodic.setdefault(self.labels[leaf], {}).setdefault(p, 0)
                self.periodic[self.labels[leaf]][p] += flt(e["value"])

    # =====================================================
    # PERIOD
    # =====================================================

    def get_period(self, d):
        if self.filters.range == "Monthly":
            return f"{self.months[d.month - 1]} {d.year}"
        if self.filters.range == "Quarterly":
            return f"Q{((d.month - 1)//3)+1} {d.year}"
        return str(get_fiscal_year(d)[0])

    def get_period_date_ranges(self):
        from_date = getdate(self.filters.from_date)
        to_date = getdate(self.filters.to_date)

        step = 1 if self.filters.range == "Monthly" else 3 if self.filters.range == "Quarterly" else 12
        self.periodic_daterange = []

        while from_date <= to_date:
            end = add_to_date(from_date, months=step, days=-1)
            self.periodic_daterange.append(min(end, to_date))
            from_date = add_days(end, 1)

    # =====================================================
    # CHART
    # =====================================================

    def get_chart_data(self):
        self.chart = {
            "type": "line",
            "data": {
                "labels": [self.get_period(d) for d in self.periodic_daterange],
                "datasets": [],
            },
        }
