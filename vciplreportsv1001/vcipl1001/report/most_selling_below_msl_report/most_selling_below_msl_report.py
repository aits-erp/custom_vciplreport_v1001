import frappe
from datetime import date


def execute(filters=None):
    filters = filters or {}

    # Default Financial Year
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
            "label": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 180
        },
        {
            "label": "Main Group",
            "fieldname": "custom_main_group",
            "fieldtype": "Data",
            "width": 180
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
        "item_code": filters.get("item_code"),
        "item_group": filters.get("item_group"),
        "include_all_items": filters.get("include_all_items", 0)
    }

    if params["include_all_items"]:
        items_query = """
            SELECT DISTINCT
                i.name AS item_code,
                i.item_name,
                i.item_group,
                i.custom_main_group,
                COALESCE(i.safety_stock, 0) AS min_stock_level
            FROM `tabItem` i
            WHERE
                i.disabled = 0
                AND i.safety_stock > 0
                AND (%(item_type)s IS NULL OR i.custom_item_type = %(item_type)s)
                AND (%(item_code)s IS NULL OR i.name = %(item_code)s)
                AND (%(item_group)s IS NULL OR i.item_group = %(item_group)s)
            ORDER BY i.name
        """

        items = frappe.db.sql(items_query, params, as_dict=True)

        if not items:
            return []

        item_codes = [i.item_code for i in items]

        bins = frappe.get_all(
            "Bin",
            filters={"item_code": ["in", item_codes]},
            fields=["item_code", "actual_qty"]
        )

        stock_map = {}
        for b in bins:
            stock_map[b.item_code] = stock_map.get(b.item_code, 0) + b.actual_qty

        sales_query = """
            SELECT
                sii.item_code,
                COALESCE(SUM(sii.amount), 0) AS total_amount,
                COALESCE(SUM(sii.qty), 0) AS total_qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE
                si.docstatus = %(docstatus)s
                AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND sii.item_code IN %(item_codes)s
            GROUP BY sii.item_code
        """

        sales_data = frappe.db.sql(sales_query, {
            "docstatus": 1,
            "from_date": params["from_date"],
            "to_date": params["to_date"],
            "item_codes": item_codes
        }, as_dict=True)

        sales_map = {s.item_code: s for s in sales_data}

        final_rows = []

        for item in items:
            total_stock = stock_map.get(item.item_code, 0)
            msl = item.min_stock_level or 0

            if total_stock <= 0:
                continue

            if total_stock >= msl:
                continue

            row = item.copy()
            row["total_stock_qty"] = total_stock
            row["shortage_qty"] = msl - total_stock
            row["details"] = "View Warehouses"

            sales = sales_map.get(item.item_code, {})
            row["total_amount"] = sales.get("total_amount", 0)
            row["total_qty"] = sales.get("total_qty", 0)

            final_rows.append(row)

        final_rows.sort(key=lambda x: x["total_amount"], reverse=True)
        return final_rows

    else:
        sales_query = """
            SELECT
                sii.item_code,
                i.item_name,
                i.item_group,
                i.custom_main_group,
                COALESCE(i.safety_stock, 0) AS min_stock_level,
                SUM(sii.amount) AS total_amount,
                SUM(sii.qty) AS total_qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
            INNER JOIN `tabItem` i ON i.name = sii.item_code
            WHERE
                si.docstatus = %(docstatus)s
                AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND i.safety_stock > 0
                AND (%(item_type)s IS NULL OR i.custom_item_type = %(item_type)s)
                AND (%(item_code)s IS NULL OR sii.item_code = %(item_code)s)
                AND (%(item_group)s IS NULL OR i.item_group = %(item_group)s)
            GROUP BY sii.item_code, i.item_name, i.item_group, i.custom_main_group, i.safety_stock
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

            if total_stock <= 0:
                continue

            if total_stock >= msl:
                continue

            r["total_stock_qty"] = total_stock
            r["shortage_qty"] = msl - total_stock
            r["details"] = "View Warehouses"

            final_rows.append(r)

        return final_rows