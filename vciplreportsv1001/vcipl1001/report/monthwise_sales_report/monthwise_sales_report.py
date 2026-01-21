import frappe
from frappe.utils import getdate, today

MONTHS = [
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


# -------------------------------
# COLUMNS
# -------------------------------
def get_columns(filters):
    columns = [{
        "label": "Customer",
        "fieldname": "customer",
        "width": 260
    }]

    selected_month = filters.get("month")

    for _, key, label in MONTHS:
        if not selected_month or selected_month == label:
            columns.append({
                "label": label,
                "fieldname": key,
                "fieldtype": "Currency",
                "width": 140
            })

    columns.append({
        "label": "Total",
        "fieldname": "total",
        "fieldtype": "Currency",
        "width": 160
    })

    return columns


# -------------------------------
# DATA
# -------------------------------
def get_data(filters):
    selected_month = filters.get("month")

    year = getdate(today()).year
    from_date = f"{year}-04-01"
    to_date = f"{year}-12-31"

    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer,
            si.posting_date,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %s AND %s
    """, (from_date, to_date), as_dict=True)

    customer_map = {}

    for inv in invoices:
        customer = inv.customer
        month_no = getdate(inv.posting_date).month
        amount = inv.grand_total

        if customer not in customer_map:
            customer_map[customer] = {
                "customer": customer,
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
