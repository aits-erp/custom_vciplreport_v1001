import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})

    data, customers = get_pivot_data(filters)
    columns = get_columns(customers)

    return columns, data


# ---------------- COLUMNS ----------------
def get_columns(customers):
    columns = [
        {
            "label": "Item Group",
            "fieldname": "item_group",
            "width": 180
        },
        {
            "label": "Main Group",
            "fieldname": "custom_main_group",
            "width": 180
        },
        {
            "label": "Sub Group",
            "fieldname": "custom_sub_group",
            "width": 180
        }
    ]

    for customer in customers:
        columns.append({
            "label": customer,
            "fieldname": frappe.scrub(customer),
            "fieldtype": "Currency",
            "width": 150
        })

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
            SUM(sii.base_net_amount) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii
            ON sii.parent = si.name
        JOIN `tabItem` i
            ON i.name = sii.item_code
        JOIN `tabCustomer` c
            ON c.name = si.customer
        LEFT JOIN `tabSales Team` st
            ON st.parent = si.name
            AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp
            ON sp.name = st.sales_person
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            c.customer_name
        ORDER BY
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group
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

        if key not in result:
            result[key] = {
                "item_group": item_group,
                "custom_main_group": main_group,
                "custom_sub_group": sub_group
            }
            for c in customers:
                result[key][frappe.scrub(c)] = 0

        result[key][frappe.scrub(customer)] += flt(row.amount)

    return list(result.values()), customers
