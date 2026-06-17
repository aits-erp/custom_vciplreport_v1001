# # Copyright (c) 2025, your company and contributors
# # For license information, please see license.txt

# import frappe

# def execute(filters=None):
#     filters = filters or {}

#     item_type  = filters.get("custom_item_type") or "Finished Goods"
#     item_group = filters.get("item_group")
#     main_group = filters.get("custom_main_group")

#     columns = get_columns()
#     data    = get_data(item_type, item_group, main_group)

#     return columns, data


# def get_columns():
#     return [
#         {"label": "Item Code",        "fieldname": "item_code",        "fieldtype": "Link", "options": "Item",       "width": 150},
#         {"label": "Main Group",       "fieldname": "custom_main_group",                                               "width": 150},
#         {"label": "Item Name",        "fieldname": "item_name",                                                       "width": 220},
#         {"label": "Item Group",       "fieldname": "item_group",        "fieldtype": "Link", "options": "Item Group", "width": 160},
#         {"label": "Current Stock",    "fieldname": "current_stock",     "fieldtype": "Float",                         "width": 130},
#         {"label": "Min Stock Level",  "fieldname": "safety_stock",      "fieldtype": "Float",                         "width": 130},
#         {"label": "Rate",             "fieldname": "rate",              "fieldtype": "Currency",                      "width": 120},
#         {"label": "Amount",           "fieldname": "amount",            "fieldtype": "Currency",                      "width": 150},
#         {"label": "Finished Goods",   "fieldname": "fg",                "fieldtype": "Float",                         "width": 130},
#         {"label": "Goods In Transit", "fieldname": "git",               "fieldtype": "Float",                         "width": 130},
#         {"label": "Bby Gala No. 014", "fieldname": "g014",             "fieldtype": "Float",                         "width": 130},
#         {"label": "Bby Gala No. 203", "fieldname": "g203",             "fieldtype": "Float",                         "width": 130},
#         {"label": "Unit-1 Shelvali",  "fieldname": "u1",               "fieldtype": "Float",                         "width": 130},
#         {"label": "Unit-2 BIDCO",     "fieldname": "u2",               "fieldtype": "Float",                         "width": 130},
#         {"label": "Unit-3 Gundale",   "fieldname": "u3",               "fieldtype": "Float",                         "width": 130},
#         {"label": "Work In Progress", "fieldname": "wip",              "fieldtype": "Float",                         "width": 130},
#         {"label": "Stores",           "fieldname": "stores",           "fieldtype": "Float",                         "width": 130},
#         # ── KBC trigger column ───────────────────────────────────────────
#         {"label": "View KBC",         "fieldname": "view_kbc",         "fieldtype": "Data",                          "width": 100},
#     ]


# def get_data(item_type, item_group, main_group):

#     conditions = ""
#     values     = [item_type]

#     if item_group:
#         conditions += " AND i.item_group = %s"
#         values.append(item_group)

#     if main_group:
#         conditions += " AND i.custom_main_group = %s"
#         values.append(main_group)

#     rows = frappe.db.sql(
#         f"""
#         SELECT
#             i.name          AS item_code,
#             i.custom_main_group,
#             i.item_name,
#             i.item_group,
#             COALESCE(i.safety_stock, 0)                     AS safety_stock,
#             COALESCE(SUM(b.actual_qty), 0)                  AS current_stock,
#             COALESCE(rate.rate, 0)                          AS rate,
#             COALESCE(SUM(b.actual_qty), 0)
#                 * COALESCE(rate.rate, 0)                    AS amount,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Finished Goods - VCIPL'    THEN b.actual_qty END), 0) AS fg,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Goods In Transit - VCIPL'  THEN b.actual_qty END), 0) AS git,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Bby Gala No. 014 - VCIPL'  THEN b.actual_qty END), 0) AS g014,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Bby Gala No. 203 - VCIPL'  THEN b.actual_qty END), 0) AS g203,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-1 Shelvali - VCIPL'   THEN b.actual_qty END), 0) AS u1,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-2 BIDCO - VCIPL'      THEN b.actual_qty END), 0) AS u2,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-3 Gundale - VCIPL'    THEN b.actual_qty END), 0) AS u3,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Work In Progress - VCIPL'  THEN b.actual_qty END), 0) AS wip,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Stores - VCIPL'            THEN b.actual_qty END), 0) AS stores
#         FROM `tabItem` i
#         LEFT JOIN `tabBin` b ON b.item_code = i.name
#         LEFT JOIN (
#             SELECT item_code, MAX(price_list_rate) AS rate
#             FROM `tabItem Price`
#             WHERE price_list = 'Standard Selling'
#               AND selling = 1
#             GROUP BY item_code
#         ) rate ON rate.item_code = i.name
#         WHERE
#             i.disabled      = 0
#             AND i.is_stock_item = 1
#             AND i.custom_item_type = %s
#             {conditions}
#         GROUP BY
#             i.name, i.custom_main_group, i.item_name,
#             i.item_group, i.safety_stock, rate.rate
#         ORDER BY current_stock DESC
#         """,
#         values,
#         as_dict=True,
#     )

#     for r in rows:
#         r["view_kbc"] = "View KBC"

#     return rows

# Copyright (c) 2025, your company and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}

    item_type  = filters.get("custom_item_type") or "Finished Goods"
    item_group = filters.get("item_group")
    main_group = filters.get("custom_main_group")

    columns = get_columns()
    data    = get_data(item_type, item_group, main_group)

    return columns, data


def get_columns():
    return [
        {"label": "Item Code",        "fieldname": "item_code",        "fieldtype": "Link", "options": "Item",       "width": 150},
        {"label": "Main Group",       "fieldname": "custom_main_group",                                               "width": 150},
        {"label": "Item Name",        "fieldname": "item_name",                                                       "width": 220},
        {"label": "Item Group",       "fieldname": "item_group",        "fieldtype": "Link", "options": "Item Group", "width": 160},
        {"label": "Current Stock",    "fieldname": "current_stock",     "fieldtype": "Float",                         "width": 130},
        {"label": "Min Stock Level",  "fieldname": "safety_stock",      "fieldtype": "Float",                         "width": 130},
        {"label": "Rate",             "fieldname": "rate",              "fieldtype": "Currency",                      "width": 120},
        {"label": "Amount",           "fieldname": "amount",            "fieldtype": "Currency",                      "width": 150},
        {"label": "Finished Goods",   "fieldname": "fg",                "fieldtype": "Float",                         "width": 130},
        {"label": "Goods In Transit", "fieldname": "git",               "fieldtype": "Float",                         "width": 130},
        {"label": "Bby Gala No. 014", "fieldname": "g014",             "fieldtype": "Float",                         "width": 130},
        {"label": "Bby Gala No. 203", "fieldname": "g203",             "fieldtype": "Float",                         "width": 130},
        {"label": "Unit-1 Shelvali",  "fieldname": "u1",               "fieldtype": "Float",                         "width": 130},
        {"label": "Unit-2 BIDCO",     "fieldname": "u2",               "fieldtype": "Float",                         "width": 130},
        {"label": "Unit-3 Gundale",   "fieldname": "u3",               "fieldtype": "Float",                         "width": 130},
        {"label": "Work In Progress", "fieldname": "wip",              "fieldtype": "Float",                         "width": 130},
        {"label": "Stores",           "fieldname": "stores",           "fieldtype": "Float",                         "width": 130},
        {"label": "Kalvert",          "fieldname": "kalvert_qty",       "fieldtype": "Float",                         "width": 120},
        {"label": "Buffing",          "fieldname": "buffing_qty",       "fieldtype": "Float",                         "width": 120},
        {"label": "Charak",           "fieldname": "charak_qty",        "fieldtype": "Float",                         "width": 120},
        # ── KBC trigger column ───────────────────────────────────────────
        {"label": "View KBC",         "fieldname": "view_kbc",         "fieldtype": "Data",                          "width": 100},
    ]


# def get_data(item_type, item_group, main_group):

#     conditions = ""
#     values     = [item_type]

#     if item_group:
#         conditions += " AND i.item_group = %s"
#         values.append(item_group)

#     if main_group:
#         conditions += " AND i.custom_main_group = %s"
#         values.append(main_group)

#     rows = frappe.db.sql(
#         f"""
#         SELECT
#             i.name          AS item_code,
#             i.custom_main_group,
#             i.item_name,
#             i.item_group,
#             COALESCE(i.safety_stock, 0)                     AS safety_stock,
#             COALESCE(SUM(b.actual_qty), 0)                  AS current_stock,
#             COALESCE(rate.rate, 0)                          AS rate,
#             COALESCE(SUM(b.actual_qty), 0)
#                 * COALESCE(rate.rate, 0)                    AS amount,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Finished Goods - VCIPL'    THEN b.actual_qty END), 0) AS fg,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Goods In Transit - VCIPL'  THEN b.actual_qty END), 0) AS git,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Bby Gala No. 014 - VCIPL'  THEN b.actual_qty END), 0) AS g014,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Bby Gala No. 203 - VCIPL'  THEN b.actual_qty END), 0) AS g203,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-1 Shelvali - VCIPL'   THEN b.actual_qty END), 0) AS u1,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-2 BIDCO - VCIPL'      THEN b.actual_qty END), 0) AS u2,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-3 Gundale - VCIPL'    THEN b.actual_qty END), 0) AS u3,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Work In Progress - VCIPL'  THEN b.actual_qty END), 0) AS wip,
#             COALESCE(SUM(CASE WHEN b.warehouse = 'Stores - VCIPL'            THEN b.actual_qty END), 0) AS stores
#         FROM `tabItem` i
#         LEFT JOIN `tabBin` b ON b.item_code = i.name
#         LEFT JOIN (
#             SELECT item_code, MAX(price_list_rate) AS rate
#             FROM `tabItem Price`
#             WHERE price_list = 'Standard Selling'
#               AND selling = 1
#             GROUP BY item_code
#         ) rate ON rate.item_code = i.name
#         WHERE
#             i.disabled         = 0
#             AND i.is_stock_item = 1
#             AND COALESCE(i.custom_is_not_stock_item, 0) = 0
#             AND i.custom_item_type = %s
#             {conditions}
#         GROUP BY
#             i.name, i.custom_main_group, i.item_name,
#             i.item_group, i.safety_stock, rate.rate
#         ORDER BY current_stock DESC
#         """,
#         values,
#         as_dict=True,
#     )

#     if not rows:
#         return []

#     # ── fetch K / B / C totals in one query ──────────────────────────
#     item_codes = [r.item_code for r in rows]

#     kbc_items = (
#         [c + "K" for c in item_codes]
#         + [c + "B" for c in item_codes]
#         + [c + "C" for c in item_codes]
#     )

#     placeholders = ", ".join(["%s"] * len(kbc_items))

#     kbc_stock = frappe.db.sql(
#         f"""
#         SELECT item_code, COALESCE(SUM(actual_qty), 0) AS total_qty
#         FROM tabBin
#         WHERE item_code IN ({placeholders})
#         GROUP BY item_code
#         """,
#         kbc_items,
#         as_dict=True,
#     )

#     kbc_map = {r.item_code: r.total_qty for r in kbc_stock}

#     for row in rows:
#         row.kalvert_qty = kbc_map.get(row.item_code + "K", 0)
#         row.buffing_qty = kbc_map.get(row.item_code + "B", 0)
#         row.charak_qty  = kbc_map.get(row.item_code + "C", 0)
#         row["view_kbc"] = "View KBC"

#     return rows

def get_data(item_type, item_group, main_group):

    conditions = ""
    values     = [item_type]

    if item_group:
        conditions += " AND i.item_group = %s"
        values.append(item_group)

    if main_group:
        conditions += " AND i.custom_main_group = %s"
        values.append(main_group)

    rows = frappe.db.sql(
        f"""
        SELECT
            i.name          AS item_code,
            i.custom_main_group,
            i.item_name,
            i.item_group,
            COALESCE(i.safety_stock, 0)                     AS safety_stock,
            COALESCE(SUM(b.actual_qty), 0)                  AS current_stock,
            COALESCE(rate.rate, 0)                          AS rate,
            COALESCE(SUM(b.actual_qty), 0)
                * COALESCE(rate.rate, 0)                    AS amount,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Finished Goods - VCIPL'    THEN b.actual_qty END), 0) AS fg,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Goods In Transit - VCIPL'  THEN b.actual_qty END), 0) AS git,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Bby Gala No. 014 - VCIPL'  THEN b.actual_qty END), 0) AS g014,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Bby Gala No. 203 - VCIPL'  THEN b.actual_qty END), 0) AS g203,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-1 Shelvali - VCIPL'   THEN b.actual_qty END), 0) AS u1,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-2 BIDCO - VCIPL'      THEN b.actual_qty END), 0) AS u2,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Unit-3 Gundale - VCIPL'    THEN b.actual_qty END), 0) AS u3,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Work In Progress - VCIPL'  THEN b.actual_qty END), 0) AS wip,
            COALESCE(SUM(CASE WHEN b.warehouse = 'Stores - VCIPL'            THEN b.actual_qty END), 0) AS stores
        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON b.item_code = i.name
        LEFT JOIN (
            SELECT item_code, MAX(price_list_rate) AS rate
            FROM `tabItem Price`
            WHERE price_list = 'Standard Selling'
              AND selling = 1
            GROUP BY item_code
        ) rate ON rate.item_code = i.name
        WHERE
            i.disabled         = 0
            AND i.is_stock_item = 1
            AND COALESCE(i.custom_is_not_stock_item, 0) = 0
            AND i.custom_item_type = %s
            {conditions}
        GROUP BY
            i.name, i.custom_main_group, i.item_name,
            i.item_group, i.safety_stock, rate.rate
        ORDER BY current_stock DESC
        """,
        values,
        as_dict=True,
    )

    if not rows:
        return []

    # ── fetch K / B / C totals in one query ──────────────────────────
    item_codes = [r.item_code for r in rows]

    kbc_items = (
        [c + "K" for c in item_codes]
        + [c + "B" for c in item_codes]
        + [c + "C" for c in item_codes]
    )

    placeholders = ", ".join(["%s"] * len(kbc_items))

    kbc_stock = frappe.db.sql(
        f"""
        SELECT item_code, COALESCE(SUM(actual_qty), 0) AS total_qty
        FROM tabBin
        WHERE item_code IN ({placeholders})
        GROUP BY item_code
        """,
        kbc_items,
        as_dict=True,
    )

    kbc_map = {r.item_code: r.total_qty for r in kbc_stock}

    for row in rows:
        row.kalvert_qty = kbc_map.get(row.item_code + "K", 0)
        row.buffing_qty = kbc_map.get(row.item_code + "B", 0)
        row.charak_qty  = kbc_map.get(row.item_code + "C", 0)
        row["view_kbc"] = "View KBC"

    return rows