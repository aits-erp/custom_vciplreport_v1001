import frappe
from datetime import date


def execute(filters=None):
    filters = filters or {}

    today = date.today()

    # DEFAULT DATE RANGE
    from_date = filters.get("from_date") or date(2025, 4, 1)
    to_date = filters.get("to_date") or today

    item_type = filters.get("custom_item_type") or "Finished Goods"
    item_group = filters.get("item_group")

    columns = get_columns()
    data = get_data(item_type, item_group, from_date, to_date)

    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 220},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 160},

        {"label": "Current Stock", "fieldname": "current_stock", "fieldtype": "Float", "width": 130},
        {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},

        {"label": "Finished Goods", "fieldname": "fg", "fieldtype": "Float", "width": 130},
        {"label": "Goods In Transit", "fieldname": "git", "fieldtype": "Float", "width": 130},
        {"label": "Bby Gala No. 014", "fieldname": "g014", "fieldtype": "Float", "width": 130},
        {"label": "Bby Gala No. 203", "fieldname": "g203", "fieldtype": "Float", "width": 130},
        {"label": "Unit-1 Shelvali", "fieldname": "u1", "fieldtype": "Float", "width": 130},
        {"label": "Unit-2 BIDCO", "fieldname": "u2", "fieldtype": "Float", "width": 130},
        {"label": "Unit-3 Gundale", "fieldname": "u3", "fieldtype": "Float", "width": 130},
        {"label": "Work In Progress", "fieldname": "wip", "fieldtype": "Float", "width": 130},
        {"label": "Stores", "fieldname": "stores", "fieldtype": "Float", "width": 130},
    ]


def get_data(item_type, item_group, from_date, to_date):

    conditions = ""
    values = [item_type, from_date, to_date]

    if item_group:
        conditions += " AND i.item_group = %s"
        values.append(item_group)

    return frappe.db.sql(
        f"""
        SELECT
            i.name AS item_code,
            i.item_name,
            i.item_group,

            SUM(b.actual_qty) AS current_stock,
            COALESCE(ip.price_list_rate, 0) AS rate,
            SUM(b.actual_qty) * COALESCE(ip.price_list_rate, 0) AS amount,

            SUM(CASE WHEN b.warehouse = 'Finished Goods - VCIPL' THEN b.actual_qty ELSE 0 END) AS fg,
            SUM(CASE WHEN b.warehouse = 'Goods In Transit - VCIPL' THEN b.actual_qty ELSE 0 END) AS git,
            SUM(CASE WHEN b.warehouse = 'Bby Gala No. 014 - VCIPL' THEN b.actual_qty ELSE 0 END) AS g014,
            SUM(CASE WHEN b.warehouse = 'Bby Gala No. 203 - VCIPL' THEN b.actual_qty ELSE 0 END) AS g203,
            SUM(CASE WHEN b.warehouse = 'Unit-1 Shelvali - VCIPL' THEN b.actual_qty ELSE 0 END) AS u1,
            SUM(CASE WHEN b.warehouse = 'Unit-2 BIDCO - VCIPL' THEN b.actual_qty ELSE 0 END) AS u2,
            SUM(CASE WHEN b.warehouse = 'Unit-3 Gundale - VCIPL' THEN b.actual_qty ELSE 0 END) AS u3,
            SUM(CASE WHEN b.warehouse = 'Work In Progress - VCIPL' THEN b.actual_qty ELSE 0 END) AS wip,
            SUM(CASE WHEN b.warehouse = 'Stores - VCIPL' THEN b.actual_qty ELSE 0 END) AS stores

        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON b.item_code = i.name

        LEFT JOIN (
            SELECT ip1.item_code, ip1.price_list_rate
            FROM `tabItem Price` ip1
            INNER JOIN (
                SELECT item_code,
                       MAX(COALESCE(valid_from, '1900-01-01')) AS latest_valid_from
                FROM `tabItem Price`
                WHERE price_list = 'Standard Selling'
                  AND selling = 1
                GROUP BY item_code
            ) ip2
              ON ip1.item_code = ip2.item_code
             AND COALESCE(ip1.valid_from, '1900-01-01') = ip2.latest_valid_from
            WHERE ip1.price_list = 'Standard Selling'
              AND ip1.selling = 1
        ) ip ON ip.item_code = i.name

        WHERE
            i.disabled = 0
            AND i.is_stock_item = 1
            AND i.custom_item_type = %s
            AND DATE(i.creation) BETWEEN %s AND %s
            {conditions}

        GROUP BY i.name, i.item_name, i.item_group, ip.price_list_rate

        HAVING SUM(b.actual_qty) != 0

        ORDER BY current_stock DESC
        """,
        values,
        as_dict=True
    )
