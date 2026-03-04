import frappe
from frappe.utils import flt
import json
from datetime import datetime


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
    (1, "jan", "January"),
    (2, "feb", "February"),
    (3, "mar", "March"),
]


def execute(filters=None):

    filters = filters or {}

    # default financial year
    if not filters.get("year"):

        today = datetime.now()

        if today.month <= 3:
            filters["year"] = str(today.year - 1)
        else:
            filters["year"] = str(today.year)

    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


def get_columns(filters):

    columns = [{
        "label": "Customer",
        "fieldname": "customer_name",
        "fieldtype": "Data",
        "width": 260
    }]

    selected_month = filters.get("month")

    for month_no, key, label in MONTHS:

        if not selected_month or selected_month == label:

            columns.append({
                "label": label,
                "fieldname": key,
                "fieldtype": "Currency",
                "width": 120
            })

    columns.append({
        "label": "Total",
        "fieldname": "total",
        "fieldtype": "Currency",
        "width": 150
    })

    return columns


def get_data(filters):

    year = filters.get("year")
    customer_group = filters.get("customer_group")
    customer = filters.get("customer")

    from_date = f"{year}-04-01"
    to_date = f"{int(year)+1}-03-31"

    conditions = ["si.docstatus = 1"]

    if customer_group:
        conditions.append("si.customer_group = %(customer_group)s")

    if customer:
        conditions.append("si.customer = %(customer)s")

    where_clause = " AND ".join(conditions)

    invoices = frappe.db.sql(f"""
        SELECT
            si.name AS invoice,
            si.customer_name,
            si.posting_date,
            si.grand_total AS amount,
            MONTH(si.posting_date) AS month_no
        FROM `tabSales Invoice` si
        WHERE {where_clause}
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY si.customer_name
    """, {
        "from_date": from_date,
        "to_date": to_date,
        "customer_group": customer_group,
        "customer": customer
    }, as_dict=True)

    customer_data = {}
    month_totals = {key: 0 for _, key, _ in MONTHS}

    for inv in invoices:

        cust = inv.customer_name
        month_no = inv.month_no
        amount = flt(inv.amount)

        if cust not in customer_data:

            customer_data[cust] = {
                "customer_name": cust,
                "total": 0
            }

            for m_no, key, label in MONTHS:
                customer_data[cust][key] = 0
                customer_data[cust][f"{key}_drill"] = []

        for m_no, key, label in MONTHS:

            if month_no == m_no:

                customer_data[cust][key] += amount
                customer_data[cust]["total"] += amount

                customer_data[cust][f"{key}_drill"].append({
                    "invoice": inv.invoice,
                    "date": str(inv.posting_date),
                    "amount": amount
                })

                month_totals[key] += amount
                break

    result = []

    for cust, data in customer_data.items():

        row = {
            "customer_name": cust,
            "total": data["total"]
        }

        for m_no, key, label in MONTHS:
            row[key] = data[key]
            row[f"{key}_drill"] = json.dumps(data[f"{key}_drill"])

        result.append(row)

    result.sort(key=lambda x: x["customer_name"])

    if result:

        summary = {
            "customer_name": "<b>GRAND TOTAL</b>",
            "is_total_row": 1,
            "total": sum(x["total"] for x in result)
        }

        for m_no, key, label in MONTHS:
            summary[key] = month_totals[key]
            summary[f"{key}_drill"] = json.dumps([])

        result.append(summary)

    return result