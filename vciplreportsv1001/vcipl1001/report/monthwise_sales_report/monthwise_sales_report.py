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


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
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


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):
    selected_month = filters.get("month")

    # Current year Apr–Dec
    year = getdate(today()).year
    from_date = f"{year}-04-01"
    to_date = f"{year}-12-31"

    sales_orders = frappe.db.sql("""
        SELECT
            so.name,
            so.customer,
            so.transaction_date,
            (so.grand_total * (1 - IFNULL(so.per_billed, 0) / 100)) AS pending
        FROM `tabSales Order` so
        WHERE so.docstatus = 1
          AND so.status NOT IN ('Closed', 'Completed')
          AND so.transaction_date BETWEEN %s AND %s
    """, (from_date, to_date), as_dict=True)

    customer_map = {}

    for so in sales_orders:
        if not so.pending or so.pending <= 0:
            continue

        customer = so.customer
        month_no = getdate(so.transaction_date).month
        pending = so.pending

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
                customer_map[customer][key] += pending
                customer_map[customer]["total"] += pending
                customer_map[customer][key + "_drill"].append({
                    "so": so.name,
                    "date": str(so.transaction_date),
                    "amount": float(pending)
                })

    result = []
    for row in customer_map.values():
        for _, key, _ in MONTHS:
            row[key + "_drill"] = frappe.as_json(row[key + "_drill"])
        result.append(row)

    return result
