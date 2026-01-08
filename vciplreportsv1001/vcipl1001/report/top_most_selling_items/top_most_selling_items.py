import frappe
from datetime import date


def execute(filters=None):
    filters = filters or {}

    # ---------------- FINANCIAL YEAR ----------------
    today = date.today()
    fy_year = today.year if today.month > 3 else today.year - 1

    from_date = date(fy_year, 4, 1)
    to_date = date(fy_year + 1, 3, 31)

    filters["from_date"] = from_date
    filters["to_date"] = to_date

    return get_columns(), get_data(filters)


# -------------------- COLUMNS --------------------
def get_columns():
    return [
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150
        },
        {
            "label": "Total Sales Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total Sold Qty",
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "Total Stock Qty",
            "fieldname": "total_stock_qty",
            "fieldtype": "Float",
            "width": 140
        }
    ]


# -------------------- DATA --------------------
def get_data(filters):
    limit = int(filters.get("record_limit") or 50)

    params = {
        "docstatus": 1,
        "from_date": filters["from_date"],
        "to_date": filters["to_date"],
        "item_type": filters.get("custom_item_type")
    }

    # ---------------- SALES QUERY ----------------
    sales_query = f"""
        SELECT
            sii.item_code,
            i.item_name,
            i.item_group,
            SUM(sii.amount) AS total_amount,
            SUM(sii.qty) AS total_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE
            si.docstatus = %(docstatus)s
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND (%(item_type)s IS NULL OR i.custom_item_type = %(item_type)s)
        GROUP BY sii.item_code, i.item_name, i.item_group
        ORDER BY total_amount DESC
        LIMIT {limit}
    """

    rows = frappe.db.sql(sales_query, params, as_dict=True)

    if not rows:
        return []

    item_codes = [r["item_code"] for r in rows]

    # ---------------- STOCK ----------------
    bins = frappe.get_all(
        "Bin",
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"]
    )

    stock_map = {}
    for b in bins:
        stock_map[b.item_code] = stock_map.get(b.item_code, 0) + b.actual_qty

    for r in rows:
        r["total_stock_qty"] = stock_map.get(r["item_code"], 0)

    return rows
