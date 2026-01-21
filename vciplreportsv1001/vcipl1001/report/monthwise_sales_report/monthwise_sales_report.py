import frappe
from frappe.utils import getdate

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
    fiscal_year = filters.get("fiscal_year")
    selected_month = filters.get("month")

    fy = frappe.db.get_value(
        "Fiscal Year",
        fiscal_year,
        ["year_start_date", "year_end_date"],
        as_dict=True
    )

    sales_orders = frappe.db.sql("""
        SELECT
            so.name,
            so.customer,
            so.transaction_date,
            (so.grand_total - so.billed_amount) AS pending
        FROM `tabSales Order` so
        WHERE so.docstatus = 1
          AND so.status NOT IN ('Closed', 'Completed')
          AND so.transaction_date BETWEEN %s AND %s
    """, (fy.year_start_date, fy.year_end_date), as_dict=True)

    cust_map = {}

    for so in sales_orders:
        customer = so.customer
        month_no = getdate(so.transaction_date).month
        pending = so.pending or 0

        if customer not in cust_map:
            cust_map[customer] = {
                "customer": customer,
                "total": 0
            }
            for _, key, _ in MONTHS:
                cust_map[customer][key] = 0
                cust_map[customer][key + "_drill"] = []

        for m_no, key, label in MONTHS:
            if month_no == m_no and (not selected_month or selected_month == label):
                cust_map[customer][key] += pending
                cust_map[customer]["total"] += pending
                cust_map[customer][key + "_drill"].append({
                    "so": so.name,
                    "date": str(so.transaction_date),
                    "amount": float(pending)
                })

    # serialize drill data
    result = []
    for row in cust_map.values():
        for _, key, _ in MONTHS:
            row[key + "_drill"] = frappe.as_json(row[key + "_drill"])
        result.append(row)

    return result
