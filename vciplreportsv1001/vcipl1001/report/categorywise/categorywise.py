import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 100},
        {"label": "Main Group", "fieldname": "main_group", "fieldtype": "Data", "width": 150},
        {"label": "Parent Sales Person", "fieldname": "parent_sales_person", "fieldtype": "Data", "width": 180},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 160},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 120},
        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 120},
        {"label": "Achieved %", "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]


def get_data(filters):

    months = [
        (1, "January", "custom_january"),
        (2, "February", "custom_february"),
        (3, "March", "custom_march"),
        (4, "April", "custom_april"),
        (5, "May", "custom_may_"),
        (6, "June", "custom_june"),
        (7, "July", "custom_july"),
        (8, "August", "custom_august"),
        (9, "September", "custom_september"),
        (10, "October", "custom_october"),
        (11, "November", "custom_november"),
        (12, "December", "custom_december"),
    ]

    data = []

    sales_team = frappe.db.sql("""
        SELECT
            st.parent AS customer,
            st.sales_person,
            st.custom_january,
            st.custom_february,
            st.custom_march,
            st.custom_april,
            st.custom_may_,
            st.custom_june,
            st.custom_july,
            st.custom_august,
            st.custom_september,
            st.custom_october,
            st.custom_november,
            st.custom_december,
            sp.parent_sales_person
        FROM `tabSales Team` st
        LEFT JOIN `tabSales Person` sp
        ON sp.name = st.sales_person
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    for row in sales_team:

        if filters.get("parent_sales_person") and row.parent_sales_person != filters.get("parent_sales_person"):
            continue

        for month_no, month_name, field in months:

            target = float(row.get(field) or 0)

            achieved = frappe.db.sql("""
                SELECT SUM(sii.base_net_amount)
                FROM `tabSales Invoice` si
                JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
                JOIN `tabItem` item ON item.name = sii.item_code
                JOIN `tabSales Team` st ON st.parent = si.name
                WHERE si.docstatus = 1
                AND st.sales_person = %(sales_person)s
                AND MONTH(si.posting_date) = %(month)s
                AND (%(main_group)s IS NULL OR item.custom_main_group = %(main_group)s)
            """, {
                "sales_person": row.sales_person,
                "month": month_no,
                "main_group": filters.get("custom_main_group")
            })

            achieved = float(achieved[0][0] or 0)

            percentage = 0
            if target > 0:
                percentage = (achieved / target) * 100

            data.append({
                "month": month_name,
                "main_group": filters.get("custom_main_group"),
                "parent_sales_person": row.parent_sales_person,
                "customer": row.customer,
                "sales_person": row.sales_person,
                "target": target,
                "achieved": achieved,
                "percentage": percentage
            })

    return data