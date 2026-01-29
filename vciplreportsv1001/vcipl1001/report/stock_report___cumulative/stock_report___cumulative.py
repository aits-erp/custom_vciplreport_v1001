import frappe
from datetime import date


def execute(filters=None):
    filters = filters or {}

    # -----------------------------
    # DEFAULT FINANCIAL YEAR (APRIL → MARCH)
    # -----------------------------
    today = date.today()
    fy_year = today.year if today.month >= 4 else today.year - 1

    filters.setdefault("from_date", date(fy_year, 4, 1))
    filters.setdefault("to_date", date(fy_year + 1, 3, 31))

    return get_columns(), get_data(filters)


def get_columns():
    return [
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 160
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 300
        },
        {
            "label": "Total Stock Qty",
            "fieldname": "total_stock_qty",
            "fieldtype": "Float",
            "width": 140
        },
        {
            "label": "Item Rate",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Amount (Qty × Rate)",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": "Warehouses",
            "fieldname": "details",
            "fieldtype": "Data",
            "width": 140
        }
    ]


def get_data(filters):

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # -----------------------------
    # FETCH ITEMS BY CREATION DATE
    # -----------------------------
    items = frappe.db.sql("""
        SELECT
            name AS item_code,
            item_name
        FROM `tabItem`
        WHERE disabled = 0
          AND is_stock_item = 1
          AND DATE(creation) BETWEEN %(from_date)s AND %(to_date)s
    """, {
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=True)

    if not items:
        return []

    item_codes = [i.item_code for i in items]

    # -----------------------------
    # FETCH STOCK FROM BIN
    # -----------------------------
    bins = frappe.get_all(
        "Bin",
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"]
    )

    stock_map = {}
    for b in bins:
        stock_map[b.item_code] = stock_map.get(b.item_code, 0) + b.actual_qty

    # -----------------------------
    # FETCH ITEM PRICES (STANDARD SELLING)
    # -----------------------------
    prices = frappe.db.sql("""
        SELECT
            item_code,
            rate
        FROM `tabItem Price`
        WHERE price_list = 'Standard Selling'
          AND selling = 1
          AND (valid_from IS NULL OR valid_from <= CURDATE())
          AND (valid_upto IS NULL OR valid_upto >= CURDATE())
    """, as_dict=True)

    price_map = {}
    for p in prices:
        price_map[p.item_code] = p.rate

    # -----------------------------
    # FINAL DATA
    # -----------------------------
    final_rows = []

    for i in items:
        qty = stock_map.get(i.item_code, 0)
        rate = price_map.get(i.item_code, 0)

        i["total_stock_qty"] = qty
        i["rate"] = rate
        i["amount"] = qty * rate
        i["details"] = "View Warehouses"

        final_rows.append(i)

    return final_rows
