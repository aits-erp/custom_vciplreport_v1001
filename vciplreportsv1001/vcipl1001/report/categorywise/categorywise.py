import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [

        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 110},

        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},

        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},

        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 130},

        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 130},

        {"label": "Territory", "fieldname": "territory", "fieldtype": "Data", "width": 170},

        {"label": "Head Sales Code", "fieldname": "head_sales", "fieldtype": "Data", "width": 140},

        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 120},

        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 120},

        {"label": "Achieved %", "fieldname": "percentage", "fieldtype": "Percent", "width": 120}

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

    conditions = ""

    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"

    if filters.get("custom_main_group"):
        conditions += " AND item.custom_main_group = %(custom_main_group)s"

    sales_team = frappe.db.sql("""

        SELECT
            st.parent as customer,
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
            sp.parent_sales_person,
            sp.custom_region,
            sp.custom_location,
            sp.custom_territory_name,
            sp.custom_head_sales_code

        FROM `tabSales Team` st

        LEFT JOIN `tabSales Person` sp
        ON sp.name = st.sales_person

    """, as_dict=True)

    data = []

    for row in sales_team:

        for month_no, month_name, field in months:

            target = row.get(field) or 0

            achieved = frappe.db.sql(f"""

                SELECT SUM(sii.base_net_amount)

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
                AND st.sales_person = %(sales_person)s
                AND MONTH(si.posting_date) = %(month)s
                {conditions}

            """, {
                "sales_person": row.sales_person,
                "month": month_no,
                "custom_main_group": filters.get("custom_main_group"),
                "parent_sales_person": filters.get("parent_sales_person")
            })

            achieved = achieved[0][0] or 0

            percentage = 0

            if target:
                percentage = (achieved / target) * 100

            data.append({

                "month": month_name,
                "customer": row.customer,
                "sales_person": row.sales_person,
                "region": row.custom_region,
                "location": row.custom_location,
                "territory": row.custom_territory_name,
                "head_sales": row.custom_head_sales_code,
                "target": target,
                "achieved": achieved,
                "percentage": percentage

            })

    return data