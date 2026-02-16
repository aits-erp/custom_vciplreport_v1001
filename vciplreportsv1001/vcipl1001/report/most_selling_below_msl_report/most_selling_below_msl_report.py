# import frappe
# from datetime import date


# def execute(filters=None):
#     filters = filters or {}

#     today = date.today()
#     fy_year = today.year if today.month > 3 else today.year - 1

#     filters["from_date"] = date(fy_year, 4, 1)
#     filters["to_date"] = date(fy_year + 1, 3, 31)

#     return get_columns(), get_data(filters)


# def get_columns():
#     return [
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 180
#         },
#         {
#             "label": "Item Name",
#             "fieldname": "item_name",
#             "fieldtype": "Data",
#             "width": 320
#         },
#         {
#             "label": "Total Sales Amount",
#             "fieldname": "total_amount",
#             "fieldtype": "Currency",
#             "width": 150
#         },
#         {
#             "label": "Total Sold Qty",
#             "fieldname": "total_qty",
#             "fieldtype": "Float",
#             "width": 120
#         },
#         {
#             "label": "Total Stock Qty",
#             "fieldname": "total_stock_qty",
#             "fieldtype": "Float",
#             "width": 120
#         },
#         {
#             "label": "Minimum Stock Level",
#             "fieldname": "min_stock_level",
#             "fieldtype": "Float",
#             "width": 150
#         },
#         {
#             "label": "Shortage Qty",
#             "fieldname": "shortage_qty",
#             "fieldtype": "Float",
#             "width": 120
#         },
#         {
#             "label": "Warehouses",
#             "fieldname": "details",
#             "fieldtype": "Data",
#             "width": 120
#         }
#     ]


# def get_data(filters):
#     params = {
#         "docstatus": 1,
#         "from_date": filters["from_date"],
#         "to_date": filters["to_date"],
#         "item_type": filters.get("custom_item_type"),
#         "item_code": filters.get("item_code")
#     }

#     sales_query = """
#         SELECT
#             sii.item_code,
#             i.item_name,
#             COALESCE(i.safety_stock, 0) AS min_stock_level,
#             SUM(sii.amount) AS total_amount,
#             SUM(sii.qty) AS total_qty
#         FROM `tabSales Invoice Item` sii
#         INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
#         INNER JOIN `tabItem` i ON i.name = sii.item_code
#         WHERE
#             si.docstatus = %(docstatus)s
#             AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
#             AND (%(item_type)s IS NULL OR i.custom_item_type = %(item_type)s)
#             AND (%(item_code)s IS NULL OR sii.item_code = %(item_code)s)
#         GROUP BY sii.item_code, i.item_name, i.safety_stock
#         ORDER BY total_amount DESC
#     """ 

#     rows = frappe.db.sql(sales_query, params, as_dict=True)
#     if not rows:
#         return []

#     item_codes = [r.item_code for r in rows]

#     bins = frappe.get_all(
#         "Bin",
#         filters={"item_code": ["in", item_codes]},
#         fields=["item_code", "actual_qty"]
#     )

#     stock_map = {}
#     for b in bins:
#         stock_map[b.item_code] = stock_map.get(b.item_code, 0) + b.actual_qty

#     final_rows = []
#     for r in rows:
#         total_stock = stock_map.get(r.item_code, 0)
#         msl = r.min_stock_level or 0

#         if total_stock <= 0:
#             continue

#         if total_stock >= msl:
#             continue

#         r["total_stock_qty"] = total_stock
#         r["shortage_qty"] = msl - total_stock
#         r["details"] = "View Warehouses"

#         final_rows.append(r)

#     return final_rows

import frappe
from datetime import date


def execute(filters=None):
    filters = filters or {}

    # If user does not select date range → default Financial Year
    if not filters.get("from_date") or not filters.get("to_date"):
        today = date.today()
        fy_year = today.year if today.month > 3 else today.year - 1

        filters["from_date"] = date(fy_year, 4, 1)
        filters["to_date"] = date(fy_year + 1, 3, 31)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 320
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
            "width": 120
        },
        {
            "label": "Minimum Stock Level",
            "fieldname": "min_stock_level",
            "fieldtype": "Float",
            "width": 150
        },
        {
            "label": "Shortage Qty",
            "fieldname": "shortage_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "Warehouses",
            "fieldname": "details",
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    params = {
        "docstatus": 1,
        "from_date": filters["from_date"],
        "to_date": filters["to_date"],
        "item_type": filters.get("custom_item_type"),
        "item_code": filters.get("item_code")
    }

    sales_query = """
        SELECT
            sii.item_code,
            i.item_name,
            COALESCE(i.safety_stock, 0) AS min_stock_level,
            SUM(sii.amount) AS total_amount,
            SUM(sii.qty) AS total_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE
            si.docstatus = %(docstatus)s
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND (%(item_type)s IS NULL OR i.custom_item_type = %(item_type)s)
            AND (%(item_code)s IS NULL OR sii.item_code = %(item_code)s)
        GROUP BY sii.item_code, i.item_name, i.safety_stock
        ORDER BY total_amount DESC
    """

    rows = frappe.db.sql(sales_query, params, as_dict=True)

    if not rows:
        return []

    item_codes = [r.item_code for r in rows]

    bins = frappe.get_all(
        "Bin",
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"]
    )

    stock_map = {}

    for b in bins:
        stock_map[b.item_code] = stock_map.get(b.item_code, 0) + b.actual_qty

    final_rows = []

    for r in rows:
        total_stock = stock_map.get(r.item_code, 0)
        msl = r.min_stock_level or 0

        # Skip items with no stock
        if total_stock <= 0:
            continue

        # Skip items above minimum stock level
        if total_stock >= msl:
            continue

        r["total_stock_qty"] = total_stock
        r["shortage_qty"] = msl - total_stock
        r["details"] = "View Warehouses"

        final_rows.append(r)

    return final_rows
