# import frappe
# from frappe.utils import flt
# import json


# def execute(filters=None):
#     filters = frappe._dict(filters or {})

#     data, customers = get_pivot_data(filters)
#     columns = get_columns(customers)

#     return columns, data


# # ---------------- COLUMNS ----------------
# def get_columns(customers):
#     columns = [
#         {"label": "Item Group", "fieldname": "item_group", "width": 180},
#         {"label": "Main Group", "fieldname": "custom_main_group", "width": 180},
#         {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 180}
#     ]

#     for customer in customers:
#         columns.append({
#             "label": customer,
#             "fieldname": frappe.scrub(customer),
#             "fieldtype": "Currency",
#             "width": 150
#         })

#     # hidden popup column
#     columns.append({"fieldname": "popup_data", "hidden": 1})

#     return columns


# # ---------------- DATA ----------------
# def get_pivot_data(filters):

#     conditions = ""
#     values = {
#         "from_date": filters.from_date,
#         "to_date": filters.to_date
#     }

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

#     raw_data = frappe.db.sql(
#         f"""
#         SELECT
#             i.item_group,
#             i.custom_main_group,
#             i.custom_sub_group,
#             c.customer_name,
#             sii.item_name,
#             sii.qty,
#             sii.base_net_amount AS amount,
#             si.name AS invoice
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         JOIN `tabItem` i ON i.name = sii.item_code
#         JOIN `tabCustomer` c ON c.name = si.customer
#         LEFT JOIN `tabSales Team` st
#             ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
#         LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
#         WHERE si.docstatus = 1
#           AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
#           {conditions}
#         """,
#         values,
#         as_dict=True
#     )

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
#                 "custom_sub_group": sub_group,
#                 "popup_data": {}
#             }
#             for c in customers:
#                 result[key][frappe.scrub(c)] = 0
#                 result[key]["popup_data"][frappe.scrub(c)] = []

#         result[key][frappe.scrub(customer)] += flt(row.amount)

#         result[key]["popup_data"][frappe.scrub(customer)].append({
#             "invoice": row.invoice,
#             "item_name": row.item_name,
#             "qty": row.qty,
#             "amount": row.amount
#         })

#     for k in result:
#         result[k]["popup_data"] = json.dumps(result[k]["popup_data"])

#     return list(result.values()), customers

import frappe
from frappe.utils import flt
import json


def execute(filters=None):
    filters = frappe._dict(filters or {})

    data, customers = get_pivot_data(filters)
    columns = get_columns(customers)

    return columns, data


# ---------------- COLUMNS ----------------
def get_columns(customers):
    columns = [
        {"label": "Item Group", "fieldname": "item_group", "width": 180},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 180},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 180}
    ]

    for customer in customers:
        columns.append({
            "label": customer,
            "fieldname": frappe.scrub(customer),
            "fieldtype": "Currency",
            "width": 150
        })

    columns.append({"fieldname": "popup_data", "hidden": 1})

    return columns


# ---------------- DATA ----------------
def get_pivot_data(filters):

    conditions = ""
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.customer:
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.customer

    if filters.item_group:
        conditions += " AND i.item_group = %(item_group)s"
        values["item_group"] = filters.item_group

    if filters.custom_main_group:
        conditions += " AND i.custom_main_group = %(custom_main_group)s"
        values["custom_main_group"] = filters.custom_main_group

    if filters.custom_sub_group:
        conditions += " AND i.custom_sub_group = %(custom_sub_group)s"
        values["custom_sub_group"] = filters.custom_sub_group

    if filters.custom_item_type:
        conditions += " AND i.custom_item_type = %(custom_item_type)s"
        values["custom_item_type"] = filters.custom_item_type

    if filters.parent_sales_person:
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.parent_sales_person

    raw_data = frappe.db.sql(
        f"""
        SELECT
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            c.customer_name,
            sii.item_name,
            sii.qty,
            sii.base_net_amount AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st
            ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        """,
        values,
        as_dict=True
    )

    customers = sorted({row.customer_name for row in raw_data})
    result = {}

    for row in raw_data:

        item_group = row.item_group or "Undefined"
        main_group = row.custom_main_group or "Undefined"
        sub_group = row.custom_sub_group or "Undefined"
        customer = row.customer_name

        key = f"{item_group}::{main_group}::{sub_group}"
        cust = frappe.scrub(customer)

        if key not in result:
            result[key] = {
                "item_group": item_group,
                "custom_main_group": main_group,
                "custom_sub_group": sub_group,
                "popup_data": {}
            }
            for c in customers:
                sc = frappe.scrub(c)
                result[key][sc] = 0
                result[key]["popup_data"][sc] = {}

        # pivot amount
        result[key][cust] += flt(row.amount)

        # aggregate popup by item
        items = result[key]["popup_data"][cust]

        if row.item_name not in items:
            items[row.item_name] = {"item_name": row.item_name, "qty": 0, "amount": 0}

        items[row.item_name]["qty"] += flt(row.qty)
        items[row.item_name]["amount"] += flt(row.amount)

    # convert dict → list + totals
    for k in result:
        for cust in result[k]["popup_data"]:
            item_list = list(result[k]["popup_data"][cust].values())

            total_qty = sum(i["qty"] for i in item_list)
            total_amt = sum(i["amount"] for i in item_list)

            item_list.append({
                "item_name": "<b>Total</b>",
                "qty": total_qty,
                "amount": total_amt
            })

            result[k]["popup_data"][cust] = item_list

        result[k]["popup_data"] = json.dumps(result[k]["popup_data"])

    return list(result.values()), customers
