# import frappe

# MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
#           "Jul","Aug","Sep","Oct","Nov","Dec"]

# MONTH_FIELD_MAP = {
#     1: "custom_january",
#     2: "custom_february",
#     3: "custom_march",
#     4: "custom_april",
#     5: "custom_may_",
#     6: "custom_june",
#     7: "custom_july",
#     8: "custom_august",
#     9: "custom_september",
#     10: "custom_october",
#     11: "custom_november",
#     12: "custom_december"
# }


# def execute(filters=None):
#     filters = frappe._dict(filters or {})
#     return get_columns(), get_data(filters)


# def get_columns():
#     return [
#         {"label": "Month", "fieldname": "month", "width": 90},
#         {"label": "TSO", "fieldname": "tso", "width": 150},
#         {"label": "Sales Person", "fieldname": "sales_person", "width": 180},
#         {"label": "Customer", "fieldname": "customer", "width": 200},
#         {"label": "Category", "fieldname": "category", "width": 150},
#         {"label": "Main Group", "fieldname": "main_group", "width": 150},
#         {"label": "Item", "fieldname": "item", "width": 180},
#         {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
#         {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
#         {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 120},
#     ]


# def get_data(filters):

#     conditions = ""
#     values = {}

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
#         values["from_date"] = filters.get("from_date")
#         values["to_date"] = filters.get("to_date")

#     if filters.get("company"):
#         conditions += " AND si.company = %(company)s"
#         values["company"] = filters.get("company")

#     # ✅ CHECK Sales Person field
#     sp_fields = [f.fieldname for f in frappe.get_meta("Sales Person").fields]

#     if "custom_territory" in sp_fields:
#         tso_field = "sp.custom_territory"
#     else:
#         tso_field = "st.sales_person"

#     # ✅ CHECK Item field
#     item_fields = [f.fieldname for f in frappe.get_meta("Item").fields]

#     if "custom_main_group" in item_fields:
#         main_group_field = "i.custom_main_group"
#     else:
#         main_group_field = "''"

#     # ✅ FINAL QUERY (FULL SAFE)
#     data = frappe.db.sql(f"""
#         SELECT
#             MONTH(si.posting_date) as month,
#             {tso_field} as tso,
#             st.sales_person as sales_person,
#             si.customer as customer_id,
#             si.customer_name as customer,
#             sii.item_group as category,
#             {main_group_field} as main_group,
#             sii.item_name as item,
#             SUM(sii.amount) as amount
#         FROM `tabSales Invoice` si
#         INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         LEFT JOIN `tabItem` i ON i.name = sii.item_code
#         LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
#         LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
#         WHERE si.docstatus = 1
#         {conditions}
#         GROUP BY
#             MONTH(si.posting_date),
#             tso,
#             st.sales_person,
#             si.customer,
#             sii.item_group,
#             main_group,
#             sii.item_name
#         ORDER BY MONTH(si.posting_date)
#     """, values, as_dict=1)

#     result = []

#     for row in data:

#         month = int(row.month) if row.month else None

#         target = get_target(row.customer_id, row.sales_person, month)

#         # ✅ SAFE CONVERSION
#         try:
#             target = float(target)
#         except:
#             target = 0

#         achieved = (row.amount / target * 100) if target else 0

#         result.append({
#             "month": MONTHS[month - 1] if month else "",
#             "tso": row.tso or "",
#             "sales_person": row.sales_person or "",
#             "customer": row.customer or "",
#             "category": row.category or "",
#             "main_group": row.main_group or "",
#             "item": row.item or "",
#             "amount": row.amount or 0,
#             "target": target,
#             "achieved": achieved
#         })

#     return result


# def get_target(customer, sales_person, month):

#     if not customer or not sales_person or not month:
#         return 0

#     fieldname = MONTH_FIELD_MAP.get(month)

#     if not fieldname:
#         return 0

#     target = frappe.db.get_value(
#         "Sales Team",
#         {
#             "parent": customer,
#             "sales_person": sales_person
#         },
#         fieldname
#     )

#     return target or 0

import frappe

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

FINANCIAL_YEAR_ORDER = [4,5,6,7,8,9,10,11,12,1,2,3]

MONTH_FIELD_MAP = {
    1: "custom_january",
    2: "custom_february",
    3: "custom_march",
    4: "custom_april",
    5: "custom_may_",
    6: "custom_june",
    7: "custom_july",
    8: "custom_august",
    9: "custom_september",
    10: "custom_october",
    11: "custom_november",
    12: "custom_december"
}


def execute(filters=None):
    filters = frappe._dict(filters or {})
    return get_columns(), get_data(filters)


# ✅ COLUMNS (ALL INCLUDED)
def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "width": 90},
        {"label": "TSO", "fieldname": "tso", "width": 150},
        {"label": "Sales Person", "fieldname": "sales_person", "width": 180},
        {"label": "Customer", "fieldname": "customer", "width": 200},
        {"label": "Category", "fieldname": "category", "width": 150},
        {"label": "Main Group", "fieldname": "main_group", "width": 150},
        {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 120},
    ]


def get_data(filters):

    conditions = ""
    values = {}

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
        values["company"] = filters.get("company")

    # ✅ Dynamic fields
    sp_fields = [f.fieldname for f in frappe.get_meta("Sales Person").fields]
    item_fields = [f.fieldname for f in frappe.get_meta("Item").fields]

    tso_field = "sp.custom_territory" if "custom_territory" in sp_fields else "st.sales_person"
    main_group_field = "i.custom_main_group" if "custom_main_group" in item_fields else "''"

    # ✅ MAIN QUERY (NO ITEM LEVEL)
    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            {tso_field} as tso,
            st.sales_person as sales_person,
            si.customer as customer_id,
            si.customer_name as customer,
            sii.item_group as category,
            {main_group_field} as main_group,
            SUM(sii.amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabItem` i ON i.name = sii.item_code
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY
            MONTH(si.posting_date),
            tso,
            st.sales_person,
            si.customer,
            sii.item_group,
            main_group
    """, values, as_dict=1)

    result = []

    total_amount = 0
    total_target = 0

    # ✅ SORT IN APR → MAR
    data_sorted = sorted(data, key=lambda x: FINANCIAL_YEAR_ORDER.index(int(x.month)))

    for row in data_sorted:

        month = int(row.month)

        target = get_target(row.customer_id, row.sales_person, month)

        try:
            target = float(target)
        except:
            target = 0

        achieved = (row.amount / target * 100) if target else 0

        total_amount += row.amount
        total_target += target

        result.append({
            "month": MONTHS[month - 1],
            "tso": row.tso or "",
            "sales_person": row.sales_person or "",
            "customer": row.customer or "",
            "category": row.category or "",
            "main_group": row.main_group or "",
            "amount": row.amount or 0,
            "target": target,
            "achieved": achieved
        })

    # ✅ TOTAL ROW
    overall_achieved = (total_amount / total_target * 100) if total_target else 0

    result.append({
        "month": "TOTAL",
        "tso": "",
        "sales_person": "",
        "customer": "",
        "category": "",
        "main_group": "",
        "amount": total_amount,
        "target": total_target,
        "achieved": overall_achieved
    })

    return result


def get_target(customer, sales_person, month):

    if not customer or not sales_person or not month:
        return 0

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    target = frappe.db.get_value(
        "Sales Team",
        {
            "parent": customer,
            "sales_person": sales_person
        },
        fieldname
    )

    return target or 0
