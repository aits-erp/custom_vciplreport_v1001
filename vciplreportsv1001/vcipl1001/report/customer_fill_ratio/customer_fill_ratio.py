import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    filters = filters or {}

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# ---------------- VALIDATION ----------------

def validate_filters(filters):
    if filters.get("from_date") and filters.get("to_date"):
        if date_diff(filters.to_date, filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))


# ---------------- MAIN DATA ----------------

def get_data(filters):

    conditions = []

    if filters.get("company"):
        conditions.append("so.company = %(company)s")

    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = " AND " + condition_sql

    customers = frappe.db.sql(f"""
        SELECT
            c.name,
            c.customer_name AS party,
            COUNT(DISTINCT so.name) AS order_count,
            SUM(soi.qty) AS qty,
            SUM(soi.delivered_qty) AS delivered_qty,
            SUM(soi.qty - soi.delivered_qty) AS pending_qty
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        INNER JOIN `tabCustomer` c ON c.name = so.customer
        WHERE so.docstatus = 1
        {condition_sql}
        GROUP BY c.name
    """, filters, as_dict=True)

    final = []

    for row in customers:

        row.fill_ratio = round(
            (flt(row.delivered_qty) / flt(row.qty) * 100)
            if row.qty else 0,
            2
        )

        if row.fill_ratio < 50:
            row.risk = "Critical"
        elif row.fill_ratio < 80:
            row.risk = "Warning"
        else:
            row.risk = "OK"

        row.order_popup = frappe.as_json(get_customer_orders(row.name, filters))
        final.append(row)

    return final


# ---------------- ORDER POPUP ----------------

def get_customer_orders(customer, filters):

    conditions = ["so.customer = %(customer)s"]

    if filters.get("company"):
        conditions.append("so.company = %(company)s")

    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")

    condition_sql = " AND ".join(conditions)

    params = dict(filters)
    params["customer"] = customer

    orders = frappe.db.sql(f"""
        SELECT
            so.name AS so_no,
            so.transaction_date AS so_date,
            SUM(soi.qty) AS qty,
            SUM(soi.delivered_qty) AS delivered,
            SUM(soi.qty - soi.delivered_qty) AS pending
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE so.docstatus = 1
        AND {condition_sql}
        GROUP BY so.name
    """, params, as_dict=True)

    for o in orders:
        o.fill_ratio = round(
            (flt(o.delivered) / flt(o.qty) * 100)
            if o.qty else 0,
            2
        )
        o.pending_popup = frappe.as_json(get_pending_items(o.so_no))

    return orders


# ---------------- ITEM POPUP ----------------

def get_pending_items(so):

    return frappe.db.sql("""
        SELECT
            item_name AS item,
            qty,
            delivered_qty AS delivered,
            (qty - delivered_qty) AS pending
        FROM `tabSales Order Item`
        WHERE parent = %s
    """, so, as_dict=True)


# ---------------- COLUMNS ----------------

def get_columns():

    return [
        {"label": _("Customer"), "fieldname": "party", "width": 260},
        {"label": _("Order Count"), "fieldname": "order_count", "fieldtype": "Int", "width": 120},
        {"label": _("Total Ordered"), "fieldname": "qty", "fieldtype": "Float"},
        {"label": _("Delivered"), "fieldname": "delivered_qty", "fieldtype": "Float"},
        {"label": _("Pending"), "fieldname": "pending_qty", "fieldtype": "Float"},
        {"label": _("Fill %"), "fieldname": "fill_ratio", "fieldtype": "Percent"},
        {"label": _("Risk Level"), "fieldname": "risk", "width": 120},
        {"fieldname": "order_popup", "hidden": 1},
    ]
