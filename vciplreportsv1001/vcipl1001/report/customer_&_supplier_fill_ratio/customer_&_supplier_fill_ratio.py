import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# ---------------- VALIDATION ----------------

def validate_filters(filters):
    if filters.get("from_date") and filters.get("to_date"):
        if date_diff(filters.to_date, filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))


# ---------------- MAIN REPORT ----------------

def get_data(filters):

    conditions = ""

    if filters.get("company"):
        conditions += " AND so.company = %(company)s"

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

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
        AND so.status NOT IN ('Completed','Closed','Stopped','On Hold')
        {conditions}
        GROUP BY c.name
    """, filters, as_dict=True)

    final = []

    for row in customers:

        row.fill_ratio = round(
            (flt(row.delivered_qty) / flt(row.qty) * 100)
            if row.qty else 0,
            2
        )

        row.order_popup = frappe.as_json(get_customer_orders(row.name))

        final.append(row)

    return final


# ---------------- LEVEL 2 POPUP ----------------

def get_customer_orders(customer):

    orders = frappe.db.sql("""
        SELECT
            so.name AS so_no,
            so.transaction_date AS so_date,
            SUM(soi.qty) AS qty,
            SUM(soi.delivered_qty) AS delivered,
            SUM(soi.qty - soi.delivered_qty) AS pending
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE so.customer = %s
        AND so.docstatus = 1
        AND so.status NOT IN ('Completed','Closed','Stopped','On Hold')
        GROUP BY so.name
        HAVING pending > 0
    """, customer, as_dict=True)

    for o in orders:

        o.fill_ratio = round(
            (flt(o.delivered) / flt(o.qty) * 100)
            if o.qty else 0,
            2
        )

        o.pending_popup = frappe.as_json(get_pending_items(o.so_no))

    return orders


# ---------------- LEVEL 3 POPUP ----------------

def get_pending_items(so):

    return frappe.db.sql("""
        SELECT
            item_name AS item,
            qty,
            delivered_qty AS delivered,
            (qty - delivered_qty) AS pending
        FROM `tabSales Order Item`
        WHERE parent = %s
        AND qty > delivered_qty
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
        {"fieldname": "order_popup", "hidden": 1},
    ]
