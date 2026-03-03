import frappe
from frappe.utils import getdate, flt, nowdate
import json
from datetime import datetime

# Months ordered from April to March (Financial Year)
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
    
    # Set default year to current year if not provided
    if not filters.get("year"):
        current_date = datetime.now()
        current_year = current_date.year
        # If current month is Jan-Mar, show previous year's financial year
        if current_date.month <= 3:
            filters["year"] = str(current_year - 1)
        else:
            filters["year"] = str(current_year)
    
    validate_filters(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def validate_filters(filters):
    if not filters.get("year"):
        frappe.throw("Year is required")


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns(filters):
    columns = [{
        "label": "Customer",
        "fieldname": "customer_name",
        "fieldtype": "Data",
        "width": 280
    }]

    selected_month = filters.get("month")

    for month_no, key, label in MONTHS:
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
# DATA
# --------------------------------------------------
def get_data(filters):
    selected_year = filters.get("year")
    selected_month = filters.get("month")
    customer_group = filters.get("customer_group")
    customer = filters.get("customer")

    # Financial year: April to March
    from_date = f"{selected_year}-04-01"
    to_date = f"{int(selected_year) + 1}-03-31"

    # Build conditions
    conditions = ["si.docstatus = 1"]
    if customer_group:
        conditions.append(f"si.customer_group = '{customer_group}'")
    if customer:
        conditions.append(f"si.customer = '{customer}'")
    
    where_clause = " AND ".join(conditions)

    # Get all sales invoices for the period
    invoices = frappe.db.sql(f"""
        SELECT
            si.name AS invoice,
            si.customer_name,
            si.customer,
            si.posting_date,
            si.grand_total as amount,
            MONTH(si.posting_date) as month_no
        FROM `tabSales Invoice` si
        WHERE {where_clause}
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY si.customer_name, si.posting_date
    """, {
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=True)

    # Organize data by customer and month
    customer_data = {}
    month_totals = {key: 0 for _, key, _ in MONTHS}

    for inv in invoices:
        customer_name = inv.customer_name
        month_no = inv.month_no
        amount = flt(inv.amount)

        # Initialize customer if not exists
        if customer_name not in customer_data:
            customer_data[customer_name] = {
                "customer_name": customer_name,
                "total": 0
            }
            # Initialize all months and drill fields
            for m_no, key, label in MONTHS:
                customer_data[customer_name][key] = 0
                customer_data[customer_name][f"{key}_drill"] = []

        # Find which month this invoice belongs to
        for m_no, key, label in MONTHS:
            if month_no == m_no:
                # Add to customer month total
                customer_data[customer_name][key] += amount
                customer_data[customer_name]["total"] += amount
                
                # Add drill-down data
                customer_data[customer_name][f"{key}_drill"].append({
                    "invoice": inv.invoice,
                    "date": str(inv.posting_date),
                    "amount": amount
                })
                
                # Add to month totals (for summary row)
                month_totals[key] += amount
                break

    # Prepare final data
    result = []
    
    # Add customer rows
    for customer_name, data in customer_data.items():
        row = {
            "customer_name": customer_name,
            "total": data["total"]
        }
        
        # Add month data and drill-down JSON
        for m_no, key, label in MONTHS:
            row[key] = data[key]
            # Convert drill-down list to JSON string
            if data[f"{key}_drill"]:
                row[f"{key}_drill"] = json.dumps(data[f"{key}_drill"], default=str)
            else:
                row[f"{key}_drill"] = json.dumps([])
        
        result.append(row)

    # Sort customers alphabetically
    result.sort(key=lambda x: x["customer_name"])

    # Add summary row (only if there are customers)
    if result:
        summary_row = {
            "customer_name": "<b>GRAND TOTAL</b>",
            "is_total_row": 1,
            "total": sum(row["total"] for row in result)
        }
        
        # Add month totals to summary row
        for m_no, key, label in MONTHS:
            summary_row[key] = month_totals[key]
            # Empty drill for summary row
            summary_row[f"{key}_drill"] = json.dumps([])
        
        result.append(summary_row)

    return result
