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


# # ================= EXECUTE =================
# def execute(filters=None):
#     filters = frappe._dict(filters or {})
#     return get_columns(), get_data(filters)


# # ================= COLUMNS =================
# def get_columns():
#     return [
#         {"label": "Month", "fieldname": "month", "width": 100},
#         {"label": "Head Sales Person", "fieldname": "parent_sales_person", "width": 200},  # 🔥 NEW
#         {"label": "TSO", "fieldname": "tso", "width": 180},
#         {"label": "Customer", "fieldname": "customer", "width": 220},
#         {"label": "Customer Group", "fieldname": "customer_group", "width": 200},
#         {"label": "Category", "fieldname": "category", "width": 180},
#         {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
#         {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 130},
#     ]


# # ================= DATA =================
# def get_data(filters):

#     conditions = ""
#     values = {}

#     # 🔥 DATE
#     if filters.get("from_date"):
#         conditions += " AND si.posting_date >= %(from_date)s"
#         values["from_date"] = filters.get("from_date")

#     if filters.get("to_date"):
#         conditions += " AND si.posting_date <= %(to_date)s"
#         values["to_date"] = filters.get("to_date")

#     # 🔥 COMPANY
#     if filters.get("company"):
#         conditions += " AND si.company = %(company)s"
#         values["company"] = filters.get("company")

#     # 🔥 CUSTOMER
#     if filters.get("customer"):
#         conditions += " AND si.customer = %(customer)s"
#         values["customer"] = filters.get("customer")

#     # 🔥 CUSTOMER GROUP
#     if filters.get("customer_group"):
#         conditions += " AND c.customer_group = %(customer_group)s"
#         values["customer_group"] = filters.get("customer_group")

#     # 🔥 TSO
#     if filters.get("tso"):
#         conditions += " AND st.sales_person = %(tso)s"
#         values["tso"] = filters.get("tso")

#     # 🔥 HEAD SALES PERSON FILTER
#     if filters.get("parent_sales_person"):
#         conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
#         values["parent_sales_person"] = filters.get("parent_sales_person")

#     # 🔥 CATEGORY
#     if filters.get("item_group"):
#         conditions += " AND sii.item_group = %(item_group)s"
#         values["item_group"] = filters.get("item_group")

#     data = frappe.db.sql(f"""
#         SELECT
#             MONTH(si.posting_date) as month,
#             st.sales_person as tso,
#             sp.parent_sales_person,
#             si.customer_name as customer,
#             c.customer_group,
#             sii.item_group as category,
#             si.customer as customer_id,
#             SUM(sii.amount) as amount
#         FROM `tabSales Invoice` si
#         INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         LEFT JOIN `tabCustomer` c ON c.name = si.customer
#         LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
#         LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
#         WHERE si.docstatus = 1
#         {conditions}
#         GROUP BY 
#             MONTH(si.posting_date),
#             st.sales_person,
#             sp.parent_sales_person,
#             si.customer,
#             c.customer_group,
#             sii.item_group
#         ORDER BY MONTH(si.posting_date), st.sales_person
#     """, values, as_dict=1)

#     result = []

#     total_target = 0
#     total_amount = 0

#     for row in data:

#         month = int(row.month)

#         target = get_target(row.customer_id, row.tso, month)
#         target = float(target or 0)

#         achieved = (row.amount / target * 100) if target else 0

#         total_target += target
#         total_amount += row.amount or 0

#         result.append({
#             "month": MONTHS[month - 1],
#             "parent_sales_person": row.parent_sales_person,
#             "tso": row.tso,
#             "customer": row.customer,
#             "customer_group": row.customer_group,
#             "category": row.category,
#             "target": target,
#             "achieved": achieved
#         })

#     # 🔥 TOTAL ROW
#     overall = (total_amount / total_target * 100) if total_target else 0

#     result.append({
#         "month": "TOTAL",
#         "target": total_target,
#         "achieved": overall
#     })

#     return result


# # ================= TARGET =================
# def get_target(customer, sales_person, month):

#     fieldname = MONTH_FIELD_MAP.get(month)

#     if not fieldname:
#         return 0

#     return frappe.db.get_value(
#         "Sales Team",
#         {"parent": customer, "sales_person": sales_person},
#         fieldname
#     ) or 0

import frappe
from frappe.utils import flt

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

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


# ================= EXECUTE =================
def execute(filters=None):
    filters = frappe._dict(filters or {})

    categories = get_categories()
    columns = get_columns(categories)
    data = get_data(filters, categories)

    return columns, data


# ================= GET CATEGORIES =================
def get_categories():
    return frappe.db.sql_list("""
        SELECT DISTINCT item_group 
        FROM `tabItem`
        WHERE item_group IS NOT NULL
    """)


# ================= COLUMNS =================
def get_columns(categories):

    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Head Sales Person", "fieldname": "parent_sales_person", "width": 200},
        {"label": "TSO", "fieldname": "tso", "width": 180},
        {"label": "Customer", "fieldname": "customer", "width": 220},
        {"label": "Customer Group", "fieldname": "customer_group", "width": 200},
    ]

    # 🔥 Dynamic Category Columns
    for cat in categories:
        safe_cat = cat.replace(" ", "_")

        columns.append({
            "label": f"{cat} Target",
            "fieldname": f"{safe_cat}_target",
            "fieldtype": "Currency",
            "width": 150
        })
        columns.append({
            "label": f"{cat} Achieved",
            "fieldname": f"{safe_cat}_achieved",
            "fieldtype": "Currency",
            "width": 150
        })

    return columns


# ================= DATA =================
def get_data(filters, categories):

    conditions = ""
    values = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    if filters.get("sales_person"):
        conditions += " AND st.sales_person = %(sales_person)s"
        values["sales_person"] = filters.get("sales_person")

    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            st.sales_person as tso,
            sp.parent_sales_person,
            si.customer_name as customer,
            c.customer_group,
            si.customer as customer_id,
            sii.item_group as category,
            SUM(sii.base_net_amount) as achieved
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY 
            MONTH(si.posting_date),
            st.sales_person,
            sp.parent_sales_person,
            si.customer,
            c.customer_group,
            sii.item_group
        ORDER BY 
            MONTH(si.posting_date), st.sales_person
    """, values, as_dict=1)

    result_dict = {}

    for row in data:

        key = (
            row.month,
            row.tso,
            row.customer
        )

        if key not in result_dict:
            result_dict[key] = {
                "month": MONTHS[int(row.month) - 1],
                "parent_sales_person": row.parent_sales_person,
                "tso": row.tso,
                "customer": row.customer,
                "customer_group": row.customer_group
            }

            # initialize all categories
            for cat in categories:
                safe_cat = cat.replace(" ", "_")
                result_dict[key][f"{safe_cat}_target"] = 0
                result_dict[key][f"{safe_cat}_achieved"] = 0

        month = int(row.month)
        safe_cat = row.category.replace(" ", "_")

        target = get_target(row.customer_id, row.tso, month)
        achieved = flt(row.achieved)

        result_dict[key][f"{safe_cat}_target"] = target
        result_dict[key][f"{safe_cat}_achieved"] = achieved

    return list(result_dict.values())


# ================= TARGET =================
def get_target(customer, sales_person, month):

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    return frappe.db.get_value(
        "Sales Team",
        {
            "parent": customer,
            "sales_person": sales_person
        },
        fieldname
    ) or 0