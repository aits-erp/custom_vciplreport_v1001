import frappe
from frappe.utils import formatdate, nowdate

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}


def execute(filters=None):
    filters = filters or {}
    return get_columns(filters), get_data(filters)


def get_columns(filters):
    month = filters.get("month") or formatdate(nowdate(), "MMM")

    return [
        {
            "label": "Customer",
            "fieldname": "customer_name",
            "width": 280
        },
        {
            "label": f"{month} Sales",
            "fieldname": "month_amount",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": "Total",
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 160
        },

        # 🔒 hidden drill data
        {"fieldname": "month_drill", "hidden": 1},
    ]


def get_data(filters):
    month = filters.get("month") or formatdate(nowdate(), "MMM")
    month_no = MONTH_MAP[month]

    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer AS customer_code,
            si.customer_name,
            si.posting_date,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
    """, as_dict=True)

    cust_map = {}

    for inv in invoices:
        code = inv.customer_code   # internal only
        name = inv.customer_name   # UI only

        if code not in cust_map:
            cust_map[code] = {
                "customer_name": name,
                "total": 0,
                "month_amount": 0,
                "month_list": []
            }

        cust_map[code]["total"] += inv.grand_total

        if inv.posting_date.month == month_no:
            cust_map[code]["month_amount"] += inv.grand_total
            cust_map[code]["month_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "amount": float(inv.grand_total)
            })

    result = []

    for row in cust_map.values():
        result.append({
            "customer_name": row["customer_name"],  # ✅ NAME ONLY
            "month_amount": row["month_amount"],
            "total": row["total"],
            "month_drill": frappe.as_json(row["month_list"])
        })

    return result
