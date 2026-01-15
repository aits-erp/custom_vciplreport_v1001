import frappe
from frappe.utils import flt, year_start, year_end


# ======================================================
# ENTRY POINT
# ======================================================
def execute(filters=None):
    filters = frappe._dict(filters or {})

    # ---------------- SAFE DEFAULTS ----------------
    if not filters.get("from_date"):
        filters.from_date = year_start()

    if not filters.get("to_date"):
        filters.to_date = year_end()

    if not filters.get("mode"):
        filters.mode = "Customer"   # Customer | Item

    if not filters.get("metric"):
        filters.metric = "Value"    # Value | Qty

    if not filters.get("level"):
        filters.level = "root"      # root, sub, customer, item, invoice

    columns = get_columns(filters.level)
    data = get_data(filters)

    return columns, data


# ======================================================
# COLUMNS
# ======================================================
def get_columns(level):

    if level == "invoice":
        return [
            {"label": "Invoice", "fieldname": "invoice", "width": 160},
            {"label": "Posting Date", "fieldname": "posting_date", "width": 120},
            {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        ]

    return [
        {"label": "Name", "fieldname": "name", "width": 320},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 160},
        {"label": "drill", "fieldname": "drill", "hidden": 1},
    ]


# ======================================================
# DATA ROUTER
# ======================================================
def get_data(f):
    if f.mode == "Customer":
        return customer_flow(f)
    else:
        return item_flow(f)


# ======================================================
# CUSTOMER FLOW
# Customer Group → Sub Group → Customer → Invoice
# ======================================================
def customer_flow(f):

    value_field = "base_net_total" if f.metric == "Value" else "total_qty"

    # ---------------- ROOT : CUSTOMER GROUP ----------------
    if f.level == "root":
        rows = frappe.db.sql(f"""
            SELECT
                customer_group AS name,
                SUM({value_field}) AS amount
            FROM `tabSales Invoice`
            WHERE docstatus = 1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY customer_group
        """, f, as_dict=True)

        return build(rows, "sub")

    # ---------------- SUB GROUP ----------------
    if f.level == "sub":
        rows = frappe.db.sql(f"""
            SELECT
                c.custom_sub_group AS name,
                SUM(si.{value_field}) AS amount
            FROM `tabSales Invoice` si
            JOIN `tabCustomer` c ON c.name = si.customer
            WHERE si.customer_group = %(value)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY c.custom_sub_group
        """, f, as_dict=True)

        return build(rows, "customer")

    # ---------------- CUSTOMER ----------------
    if f.level == "customer":
        rows = frappe.db.sql(f"""
            SELECT
                si.customer_name AS name,
                si.customer,
                SUM(si.{value_field}) AS amount
            FROM `tabSales Invoice` si
            JOIN `tabCustomer` c ON c.name = si.customer
            WHERE c.custom_sub_group = %(value)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY si.customer
        """, f, as_dict=True)

        out = []
        for r in rows:
            out.append({
                "name": r.name,
                "amount": flt(r.amount),
                "drill": frappe.as_json({
                    "level": "invoice",
                    "customer": r.customer
                })
            })
        return out

    # ---------------- INVOICE ----------------
    if f.level == "invoice":
        return frappe.db.sql(f"""
            SELECT
                name AS invoice,
                posting_date,
                {value_field} AS amount
            FROM `tabSales Invoice`
            WHERE customer = %(customer)s
              AND docstatus = 1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        """, f, as_dict=True)

    return []


# ======================================================
# ITEM FLOW
# Item Group → Main → Sub → Sub1 → Item → Invoice
# ======================================================
def item_flow(f):

    value_field = "base_net_amount" if f.metric == "Value" else "qty"

    # ---------------- ROOT : ITEM GROUP ----------------
    if f.level == "root":
        rows = frappe.db.sql(f"""
            SELECT
                i.item_group AS name,
                SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.item_group
        """, f, as_dict=True)

        return build(rows, "main")

    # ---------------- MAIN GROUP ----------------
    if f.level == "main":
        rows = frappe.db.sql(f"""
            SELECT
                i.custom_main_group AS name,
                SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE i.item_group = %(value)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.custom_main_group
        """, f, as_dict=True)

        return build(rows, "sub")

    # ---------------- SUB GROUP ----------------
    if f.level == "sub":
        rows = frappe.db.sql(f"""
            SELECT
                i.custom_sub_group AS name,
                SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE i.custom_main_group = %(value)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.custom_sub_group
        """, f, as_dict=True)

        return build(rows, "sub1")

    # ---------------- SUB GROUP 1 ----------------
    if f.level == "sub1":
        rows = frappe.db.sql(f"""
            SELECT
                i.custom_sub_group1 AS name,
                SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE i.custom_sub_group = %(value)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.custom_sub_group1
        """, f, as_dict=True)

        return build(rows, "item")

    # ---------------- ITEM ----------------
    if f.level == "item":
        rows = frappe.db.sql(f"""
            SELECT
                i.item_name AS name,
                sii.item_code,
                SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE i.custom_sub_group1 = %(value)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY sii.item_code
        """, f, as_dict=True)

        out = []
        for r in rows:
            out.append({
                "name": r.name,
                "amount": flt(r.amount),
                "drill": frappe.as_json({
                    "level": "invoice",
                    "item_code": r.item_code
                })
            })
        return out

    # ---------------- INVOICE ----------------
    if f.level == "invoice":
        return frappe.db.sql(f"""
            SELECT
                si.name AS invoice,
                si.posting_date,
                sii.{value_field} AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE sii.item_code = %(item_code)s
              AND si.docstatus = 1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        """, f, as_dict=True)

    return []


# ======================================================
# HELPER
# ======================================================
def build(rows, next_level):
    out = []
    for r in rows:
        out.append({
            "name": r.name or "Not Set",
            "amount": flt(r.amount),
            "drill": frappe.as_json({
                "level": next_level,
                "value": r.name
            })
        })
    return out
