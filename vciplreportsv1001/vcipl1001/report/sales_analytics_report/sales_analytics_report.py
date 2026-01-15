import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    mode = filters.get("mode", "Customer")
    level = filters.get("level", "root")
    metric = filters.get("metric", "Value")

    columns = get_columns(level)
    data = get_data(mode, level, metric, filters)

    return columns, data


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns(level):

    base = [
        {"label": "Name", "fieldname": "name", "width": 300},
        {"label": "Amount", "fieldname": "amount",
         "fieldtype": "Float", "width": 160},
        {"label": "drill", "fieldname": "drill", "hidden": 1},
    ]

    if level == "invoice":
        return [
            {"label": "Invoice", "fieldname": "invoice", "width": 160},
            {"label": "Posting Date", "fieldname": "posting_date", "width": 120},
            {"label": "Amount", "fieldname": "amount",
             "fieldtype": "Float", "width": 140},
        ]

    return base


# --------------------------------------------------
# DATA ROUTER
# --------------------------------------------------
def get_data(mode, level, metric, f):

    if mode == "Customer":
        return customer_flow(level, metric, f)
    else:
        return item_flow(level, metric, f)


# ==================================================
# CUSTOMER FLOW
# ==================================================
def customer_flow(level, metric, f):

    value_field = "base_net_amount" if metric == "Value" else "qty"

    if level == "root":
        rows = frappe.db.sql(f"""
            SELECT customer_group AS name,
                   SUM({value_field}) AS amount
            FROM `tabSales Invoice`
            WHERE docstatus=1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY customer_group
        """, f, as_dict=True)

        return build(rows, "sub_group")

    if level == "sub_group":
        rows = frappe.db.sql(f"""
            SELECT c.custom_sub_group AS name,
                   SUM(si.{value_field}) AS amount
            FROM `tabSales Invoice` si
            JOIN `tabCustomer` c ON c.name = si.customer
            WHERE si.customer_group=%(value)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY c.custom_sub_group
        """, f, as_dict=True)

        return build(rows, "customer")

    if level == "customer":
        rows = frappe.db.sql(f"""
            SELECT si.customer_name AS name,
                   SUM(si.{value_field}) AS amount,
                   si.customer AS customer
            FROM `tabSales Invoice` si
            JOIN `tabCustomer` c ON c.name = si.customer
            WHERE c.custom_sub_group=%(value)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY si.customer
        """, f, as_dict=True)

        for r in rows:
            r["drill"] = frappe.as_json({
                "level": "invoice",
                "customer": r["customer"]
            })

        return rows

    if level == "invoice":
        return frappe.db.sql(f"""
            SELECT name AS invoice,
                   posting_date,
                   {value_field} AS amount
            FROM `tabSales Invoice`
            WHERE customer=%(customer)s
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        """, f, as_dict=True)

    return []


# ==================================================
# ITEM FLOW
# ==================================================
def item_flow(level, metric, f):

    value_field = "base_net_amount" if metric == "Value" else "qty"

    if level == "root":
        rows = frappe.db.sql(f"""
            SELECT i.item_group AS name,
                   SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE si.docstatus=1
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.item_group
        """, f, as_dict=True)

        return build(rows, "main_group")

    if level == "main_group":
        rows = frappe.db.sql(f"""
            SELECT i.custom_main_group AS name,
                   SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabItem` i ON i.name = sii.item_code
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE i.item_group=%(value)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.custom_main_group
        """, f, as_dict=True)

        return build(rows, "sub_group")

    if level == "sub_group":
        rows = frappe.db.sql(f"""
            SELECT i.custom_sub_group AS name,
                   SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabItem` i ON i.name = sii.item_code
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE i.custom_main_group=%(value)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.custom_sub_group
        """, f, as_dict=True)

        return build(rows, "sub_group1")

    if level == "sub_group1":
        rows = frappe.db.sql(f"""
            SELECT i.custom_sub_group1 AS name,
                   SUM(sii.{value_field}) AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabItem` i ON i.name = sii.item_code
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE i.custom_sub_group=%(value)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY i.custom_sub_group1
        """, f, as_dict=True)

        return build(rows, "item")

    if level == "item":
        rows = frappe.db.sql(f"""
            SELECT i.item_name AS name,
                   SUM(sii.{value_field}) AS amount,
                   sii.item_code
            FROM `tabSales Invoice Item` sii
            JOIN `tabItem` i ON i.name = sii.item_code
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE i.custom_sub_group1=%(value)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY sii.item_code
        """, f, as_dict=True)

        for r in rows:
            r["drill"] = frappe.as_json({
                "level": "invoice",
                "item_code": r["item_code"]
            })

        return rows

    if level == "invoice":
        return frappe.db.sql(f"""
            SELECT si.name AS invoice,
                   si.posting_date,
                   sii.{value_field} AS amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE sii.item_code=%(item_code)s
              AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        """, f, as_dict=True)

    return []


# --------------------------------------------------
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
