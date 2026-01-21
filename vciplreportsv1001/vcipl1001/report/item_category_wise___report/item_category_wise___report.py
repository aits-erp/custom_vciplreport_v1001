import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {
            "label": "Customer Name",
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "Parent Sales Person",
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": "Main Group",
            "fieldname": "custom_main_group",
            "width": 160
        },
        {
            "label": "Sub Group",
            "fieldname": "custom_sub_group",
            "width": 160
        },
        {
            "label": "Sub Group 1",
            "fieldname": "custom_sub_group1",
            "width": 160
        },
        {
            "label": "Item Type",
            "fieldname": "custom_item_type",
            "width": 160
        },
        {
            "label": "Total Invoice Amount",
            "fieldname": "invoice_amount",
            "fieldtype": "Currency",
            "width": 180
        }
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    conditions = ""
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.customer:
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.customer

    if filters.custom_main_group:
        conditions += " AND i.custom_main_group = %(custom_main_group)s"
        values["custom_main_group"] = filters.custom_main_group

    if filters.custom_item_type:
        conditions += " AND i.custom_item_type = %(custom_item_type)s"
        values["custom_item_type"] = filters.custom_item_type

    if filters.parent_sales_person:
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.parent_sales_person

    data = frappe.db.sql(
        f"""
        SELECT
            c.customer_name,
            sp.parent_sales_person,
            i.custom_main_group,
            i.custom_sub_group,
            i.custom_sub_group1,
            i.custom_item_type,
            SUM(sii.base_net_amount) AS invoice_amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY
            c.customer_name,
            sp.parent_sales_person,
            i.custom_main_group,
            i.custom_sub_group,
            i.custom_sub_group1,
            i.custom_item_type
        ORDER BY c.customer_name
        """,
        values,
        as_dict=True
    )

    # ensure numeric safety
    for d in data:
        d.invoice_amount = flt(d.invoice_amount)

    return data
