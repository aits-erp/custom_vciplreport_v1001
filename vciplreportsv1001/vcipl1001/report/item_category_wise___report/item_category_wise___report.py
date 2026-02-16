# import frappe
# from frappe.utils import flt


# def execute(filters=None):
#     filters = frappe._dict(filters or {})

#     data, customers = get_pivot_data(filters)
#     columns = get_columns(customers)

#     return columns, data


# # --------------------------------------------------
# # COLUMNS
# # --------------------------------------------------
# def get_columns(customers):
#     columns = [
#         {
#             "label": "Item Group",
#             "fieldname": "item_group",
#             "width": 180
#         },
#         {
#             "label": "Main Group",
#             "fieldname": "custom_main_group",
#             "width": 180
#         },
#         {
#             "label": "Sub Group",
#             "fieldname": "custom_sub_group",
#             "width": 180
#         }
#     ]

#     for customer in customers:
#         columns.append({
#             "label": customer,
#             "fieldname": frappe.scrub(customer),
#             "fieldtype": "Currency",
#             "width": 150
#         })

#     return columns


# # --------------------------------------------------
# # DATA (SQL + PIVOT)
# # --------------------------------------------------
# def get_pivot_data(filters):

#     conditions = ""
#     values = {
#         "from_date": filters.from_date,
#         "to_date": filters.to_date
#     }

#     # ---------------- FILTERS ----------------
#     if filters.customer:
#         conditions += " AND si.customer = %(customer)s"
#         values["customer"] = filters.customer

#     if filters.item_group:
#         conditions += " AND i.item_group = %(item_group)s"
#         values["item_group"] = filters.item_group

#     if filters.custom_main_group:
#         conditions += " AND i.custom_main_group = %(custom_main_group)s"
#         values["custom_main_group"] = filters.custom_main_group

#     if filters.custom_sub_group:
#         conditions += " AND i.custom_sub_group = %(custom_sub_group)s"
#         values["custom_sub_group"] = filters.custom_sub_group

#     if filters.custom_item_type:
#         conditions += " AND i.custom_item_type = %(custom_item_type)s"
#         values["custom_item_type"] = filters.custom_item_type

#     if filters.parent_sales_person:
#         conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
#         values["parent_sales_person"] = filters.parent_sales_person

#     # ---------------- SQL ----------------
#     raw_data = frappe.db.sql(
#         f"""
#         SELECT
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group,
#             c.customer_name,
#             SUM(sii.base_net_amount) AS amount
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii
#             ON sii.parent = si.name
#         JOIN `tabItem` i
#             ON i.name = sii.item_code
#         JOIN `tabCustomer` c
#             ON c.name = si.customer
#         LEFT JOIN `tabSales Team` st
#             ON st.parent = si.name
#             AND st.parenttype = 'Sales Invoice'
#         LEFT JOIN `tabSales Person` sp
#             ON sp.name = st.sales_person
#         WHERE si.docstatus = 1
#           AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
#           {conditions}
#         GROUP BY
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group,
#             c.customer_name
#         ORDER BY
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group
#         """,
#         values,
#         as_dict=True
#     )

#     # ---------------- PIVOT ----------------
#     customers = sorted({row.customer_name for row in raw_data})
#     result = {}

#     for row in raw_data:
#         item_group = row.item_group or "Undefined"
#         main_group = row.custom_main_group or "Undefined"
#         sub_group = row.custom_sub_group or "Undefined"
#         customer = row.customer_name

#         key = f"{item_group}::{main_group}::{sub_group}"

#         if key not in result:
#             result[key] = {
#                 "item_group": item_group,
#                 "custom_main_group": main_group,
#                 "custom_sub_group": sub_group
#             }
#             for c in customers:
#                 result[key][frappe.scrub(c)] = 0

#         result[key][frappe.scrub(customer)] += flt(row.amount)

#     return list(result.values()), customers


# import frappe
# from frappe.utils import flt


# def execute(filters=None):
#     filters = frappe._dict(filters or {})

#     data, customers = get_pivot_data(filters)
#     columns = get_columns(customers)

#     return columns, data


# # --------------------------------------------------
# # COLUMNS
# # --------------------------------------------------
# def get_columns(customers):
#     columns = [
#         {
#             "label": "Item Group",
#             "fieldname": "item_group",
#             "width": 180
#         },
#         {
#             "label": "Main Group",
#             "fieldname": "custom_main_group",
#             "width": 180
#         },
#         {
#             "label": "Sub Group",
#             "fieldname": "custom_sub_group",
#             "width": 180
#         }
#     ]

#     for customer in customers:
#         columns.append({
#             "label": customer,
#             "fieldname": frappe.scrub(customer),
#             "fieldtype": "Currency",
#             "width": 150
#         })

#     return columns


# # --------------------------------------------------
# # DATA (SQL + PIVOT)
# # --------------------------------------------------
# def get_pivot_data(filters):

#     conditions = ""
#     values = {
#         "from_date": filters.from_date,
#         "to_date": filters.to_date
#     }

#     # ---------------- FILTERS ----------------
#     if filters.customer:
#         conditions += " AND si.customer = %(customer)s"
#         values["customer"] = filters.customer

#     if filters.item_group:
#         conditions += " AND i.item_group = %(item_group)s"
#         values["item_group"] = filters.item_group

#     if filters.custom_main_group:
#         conditions += " AND i.custom_main_group = %(custom_main_group)s"
#         values["custom_main_group"] = filters.custom_main_group

#     if filters.custom_sub_group:
#         conditions += " AND i.custom_sub_group = %(custom_sub_group)s"
#         values["custom_sub_group"] = filters.custom_sub_group

#     if filters.custom_item_type:
#         conditions += " AND i.custom_item_type = %(custom_item_type)s"
#         values["custom_item_type"] = filters.custom_item_type

#     if filters.parent_sales_person:
#         conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
#         values["parent_sales_person"] = filters.parent_sales_person

#     # ---------------- SQL ----------------
#     raw_data = frappe.db.sql(
#         f"""
#         SELECT
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group,
#             c.customer_name,
#             SUM(sii.base_net_amount) AS amount
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii
#             ON sii.parent = si.name
#         JOIN `tabItem` i
#             ON i.name = sii.item_code
#         JOIN `tabCustomer` c
#             ON c.name = si.customer
#         LEFT JOIN `tabSales Team` st
#             ON st.parent = si.name
#             AND st.parenttype = 'Sales Invoice'
#         LEFT JOIN `tabSales Person` sp
#             ON sp.name = st.sales_person
#         WHERE si.docstatus = 1
#           AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
#           {conditions}
#         GROUP BY
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group,
#             c.customer_name
#         ORDER BY
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group
#         """,
#         values,
#         as_dict=True
#     )

#     # ---------------- PIVOT ----------------
#     customers = sorted({row.customer_name for row in raw_data})
#     result = {}

#     for row in raw_data:
#         item_group = row.item_group or "Undefined"
#         main_group = row.custom_main_group or "Undefined"
#         sub_group = row.custom_sub_group or "Undefined"
#         customer = row.customer_name

#         key = f"{item_group}::{main_group}::{sub_group}"

#         if key not in result:
#             result[key] = {
#                 "item_group": item_group,
#                 "custom_main_group": main_group,
#                 "custom_sub_group": sub_group
#             }
#             for c in customers:
#                 result[key][frappe.scrub(c)] = 0

#         result[key][frappe.scrub(customer)] += flt(row.amount)

#     return list(result.values()), customers

import frappe
from frappe.utils import flt, add_years


def execute(filters=None):
    filters = frappe._dict(filters or {})
    data, customers = get_pivot_data(filters)
    columns = get_columns(customers)
    return columns, data


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns(customers):
    columns = [
        {"label": "Item Group", "fieldname": "item_group", "width": 180},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 180},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 180},
    ]

    for customer in customers:
        columns.append({
            "label": customer,
            "fieldname": frappe.scrub(customer),
            "fieldtype": "Currency",
            "width": 150
        })

    return columns


# --------------------------------------------------
# DATA (PIVOT)
# --------------------------------------------------
def get_pivot_data(filters):

    conditions = ""
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.customer:
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.customer

    raw_data = frappe.db.sql(f"""
        SELECT
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            c.customer_name,
            SUM(sii.base_net_amount) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            c.customer_name
    """, values, as_dict=True)

    customers = sorted({row.customer_name for row in raw_data})
    result = {}

    for row in raw_data:
        key = f"{row.item_group}::{row.custom_main_group}::{row.custom_sub_group}"

        if key not in result:
            result[key] = {
                "item_group": row.item_group,
                "custom_main_group": row.custom_main_group,
                "custom_sub_group": row.custom_sub_group
            }
            for c in customers:
                result[key][frappe.scrub(c)] = 0

        result[key][frappe.scrub(row.customer_name)] += flt(row.amount)

    return list(result.values()), customers


# --------------------------------------------------
# 🔥 POPUP SUMMARY API
# --------------------------------------------------
@frappe.whitelist()
def get_customer_summary(customer, from_date, to_date):

    ly_from = add_years(from_date, -1)
    ly_to = add_years(to_date, -1)

    target = frappe.db.sql("""
        SELECT SUM(
            COALESCE(custom_january,0)+COALESCE(custom_february,0)+
            COALESCE(custom_march,0)+COALESCE(custom_april,0)+
            COALESCE(custom_may_,0)+COALESCE(custom_june,0)+
            COALESCE(custom_july,0)+COALESCE(custom_august,0)+
            COALESCE(custom_september,0)+COALESCE(custom_october,0)+
            COALESCE(custom_november,0)+COALESCE(custom_december,0)
        )
        FROM `tabSales Team`
        WHERE parenttype='Customer' AND parent=%s
    """, customer)[0][0] or 0

    invoice = frappe.db.sql("""
        SELECT SUM(base_net_total)
        FROM `tabSales Invoice`
        WHERE docstatus=1
          AND customer=%s
          AND posting_date BETWEEN %s AND %s
    """, (customer, from_date, to_date))[0][0] or 0

    last_year = frappe.db.sql("""
        SELECT SUM(base_net_total)
        FROM `tabSales Invoice`
        WHERE docstatus=1
          AND customer=%s
          AND posting_date BETWEEN %s AND %s
    """, (customer, ly_from, ly_to))[0][0] or 0

    achieved = (invoice / target * 100) if target else 0

    return {
        "customer": customer,
        "target": flt(target),
        "invoice": flt(invoice),
        "achieved": flt(achieved),
        "last_year": flt(last_year)
    }
