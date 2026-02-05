import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    if not filters:
        filters = {}

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# ---------------- VALIDATION ----------------

def validate_filters(filters):

    if filters.get("from_date") and filters.get("to_date"):
        if date_diff(filters.to_date, filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))


# ---------------- DATA ----------------

def get_data(filters):

    conditions = ""

    if filters.get("company"):
        conditions += " AND so.company = %(company)s"

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    data = frappe.db.sql(f"""
        SELECT
            soi.item_code,
            soi.item_name,
            SUM(soi.qty) as total_ordered,
            SUM(soi.delivered_qty) as total_delivered,
            SUM(soi.qty - soi.delivered_qty) as total_pending,
            COUNT(DISTINCT so.name) as order_count
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE so.docstatus = 1
        AND so.status NOT IN ('Completed','Closed','Stopped','On Hold')
        {conditions}
        GROUP BY soi.item_code
        HAVING total_pending > 0
        ORDER BY total_pending DESC
    """, filters, as_dict=True)

    filtered_data = []

    for row in data:

        # calculate fill ratio
        row.fill_ratio = round(
            (flt(row.total_delivered) / flt(row.total_ordered) * 100)
            if row.total_ordered else 0,
            2
        )

        # risk classification
        if row.fill_ratio < 50:
            row.risk = "Critical"
        elif row.fill_ratio < 80:
            row.risk = "Warning"
        else:
            row.risk = "OK"

        # apply risk filter
        risk_filter = filters.get("risk_filter")

        if risk_filter == "HIGH" and row.risk != "Critical":
            continue

        if risk_filter == "Medium" and row.risk != "Warning":
            continue

        if risk_filter == "OK" and row.risk != "OK":
            continue

        filtered_data.append(row)

    return filtered_data


# ---------------- COLUMNS ----------------

def get_columns():

    return [
        {"label": _("Item Code"), "fieldname": "item_code", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 220},

        {"label": _("Total Ordered"), "fieldname": "total_ordered", "fieldtype": "Float"},
        {"label": _("Delivered"), "fieldname": "total_delivered", "fieldtype": "Float"},
        {"label": _("Pending"), "fieldname": "total_pending", "fieldtype": "Float"},

        {"label": _("Fill %"), "fieldname": "fill_ratio", "fieldtype": "Percent"},

        {"label": _("No. of Orders"), "fieldname": "order_count", "fieldtype": "Int"},

        {"label": _("Risk Level"), "fieldname": "risk", "width": 120},
    ]
