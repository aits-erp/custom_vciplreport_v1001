import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [

        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 120},

        {"label": "Main Group", "fieldname": "main_group", "fieldtype": "Data", "width": 160},

        {"label": "Parent Sales Person", "fieldname": "parent_sales_person", "fieldtype": "Data", "width": 180},

        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},

        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},

        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 130},

        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 130},

        {"label": "Achieved %", "fieldname": "percentage", "fieldtype": "Percent", "width": 120},

    ]


def get_data(filters):

    conditions = ""

    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"

    if filters.get("custom_main_group"):
        conditions += " AND item.custom_main_group = %(custom_main_group)s"


    data = frappe.db.sql(f"""

        SELECT

            MONTHNAME(si.posting_date) AS month,

            item.custom_main_group AS main_group,

            sp.parent_sales_person,

            st.parent AS customer,

            st.sales_person,

            SUM(sii.base_net_amount) AS achieved

        FROM `tabSales Invoice` si

        JOIN `tabSales Invoice Item` sii
        ON sii.parent = si.name

        JOIN `tabItem` item
        ON item.name = sii.item_code

        JOIN `tabSales Team` st
        ON st.parent = si.name

        JOIN `tabSales Person` sp
        ON sp.name = st.sales_person

        WHERE si.docstatus = 1

        {conditions}

        GROUP BY
            MONTH(si.posting_date),
            item.custom_main_group,
            sp.parent_sales_person,
            st.parent,
            st.sales_person

        ORDER BY MONTH(si.posting_date)

    """, filters, as_dict=True)


    for row in data:

        row.target = 0
        row.percentage = 0

        if row.target:
            row.percentage = (row.achieved / row.target) * 100

    return data