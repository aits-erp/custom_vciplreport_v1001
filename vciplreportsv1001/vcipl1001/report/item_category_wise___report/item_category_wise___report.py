import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})

    data, customers = get_pivot_data(filters)
    columns = get_columns(customers)

    return columns, data


# --------------------------------------------------
# COLUMNS (Main Group + Dynamic Customers)
# --------------------------------------------------
def get_columns(customers):
    columns = [
        {
            "label": "Main Group",
            "fieldname": "custom_main_group",
            "width": 200
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


# --------------------------------------------------
# DATA (SQL + PIVOT)
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

    if filters.custom_main_group:
        conditions += " AND i.custom_main_group = %(custom_main_group)s"
        values["custom_main_group"] = filters.custom_main_group

    if filters.custom_item_type:
        conditions += " AND i.custom_item_type = %(custom_item_type)s"
        values["custom_item_type"] = filters.custom_item_type

    if filters.parent_sales_person:
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.parent_sales_person

    raw_data = frappe.db.sql(
        f"""
        SELECT
            i.custom_main_group,
            c.customer_name,
            SUM(sii.base_net_amount) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st 
            ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp 
            ON sp.name = st.sales_person
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY
            i.custom_main_group,
            c.customer_name
        ORDER BY
            i.custom_main_group
        """,
        values,
        as_dict=True
    )

    # ---------------------------------------------
    # PIVOT LOGIC
    # ---------------------------------------------
    customers = sorted({d.customer_name for d in raw_data})
    result = {}

    for row in raw_data:
        main_group = row.custom_main_group or "Undefined"
        customer = row.customer_name

        if main_group not in result:
            result[main_group] = {
                "custom_main_group": main_group
            }
            for c in customers:
                result[main_group][frappe.scrub(c)] = 0

        result[main_group][frappe.scrub(customer)] += flt(row.amount)

    return list(result.values()), customers
