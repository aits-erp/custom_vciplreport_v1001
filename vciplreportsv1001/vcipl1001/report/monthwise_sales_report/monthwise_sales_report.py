import frappe
from frappe.utils import getdate

MONTHS = [
    (1, "jan", "January"),
    (2, "feb", "February"),
    (3, "mar", "March"),
    (4, "apr", "April"),
    (5, "may", "May"),
    (6, "jun", "June"),
    (7, "jul", "July"),
    (8, "aug", "August"),
    (9, "sep", "September"),
    (10, "oct", "October"),
    (11, "nov", "November"),
    (12, "dec", "December"),
]


def execute(filters=None):
    filters = filters or {}
    return get_columns(filters), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns(filters):
    columns = [{
        "label": "Customer",
        "fieldname": "customer_name",
        "width": 280
    }]

    selected_month = filters.get("month")

    for _, key, label in MONTHS:
        if not selected_month or selected_month == label:
            columns.append({
                "label": label,
                "fieldname": key,
                "fieldtype": "Currency",
                "width": 130
            })

    columns.append({
        "label": "Total",
        "fieldname": "total",
        "fieldtype": "Currency",
        "width": 160
    })

    return columns


# --------------------------------------------------
# DATA (Sales Invoice BASE)
# --------------------------------------------------
def get_data(filters):
    selected_month = filters.get("month")

    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer_name,
            si.posting_date,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
    """, as_dict=True)

    customer_map = {}

    for inv in invoices:
        customer = inv.customer_name   # ✅ CUSTOMER NAME
        month_no = getdate(inv.posting_date).month
        amount = inv.grand_total

        if customer not in customer_map:
            customer_map[customer] = {
                "customer_name": customer,
                "total": 0
            }
            for _, key, _ in MONTHS:
                customer_map[customer][key] = 0
                customer_map[customer][key + "_drill"] = []

        for m_no, key, label in MONTHS:
            if month_no == m_no and (not selected_month or selected_month == label):
                customer_map[customer][key] += amount
                customer_map[customer]["total"] += amount
                customer_map[customer][key + "_drill"].append({
                    "invoice": inv.invoice,
                    "date": str(inv.posting_date),
                    "amount": float(amount)
                })

    result = []
    for row in customer_map.values():
        for _, key, _ in MONTHS:
            row[key + "_drill"] = frappe.as_json(row[key + "_drill"])
        result.append(row)

    return result
