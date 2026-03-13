import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    columns = [

        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 120},

        {"label": "Parent Sales Person", "fieldname": "parent_sales_person", "fieldtype": "Data", "width": 200},

        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 140},

        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 140},

        {"label": "Territory", "fieldname": "territory", "fieldtype": "Data", "width": 180},

        {"label": "Head Sales Code", "fieldname": "head_sales", "fieldtype": "Data", "width": 150},

        {"label": "Target", "fieldname": "target", "fieldtype": "Float", "width": 120},

        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Float", "width": 120},

        {"label": "Achieved %", "fieldname": "percentage", "fieldtype": "Percent", "width": 120},

    ]

    return columns


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
        conditions += " AND parent_sales_person = %(parent_sales_person)s"

    sales_persons = frappe.db.sql(f"""

        SELECT
            name,
            parent_sales_person,
            custom_region,
            custom_location,
            custom_territory_name,
            custom_head_sales_code,
            custom_january,
            custom_february,
            custom_march,
            custom_april,
            custom_may_,
            custom_june,
            custom_july,
            custom_august,
            custom_september,
            custom_october,
            custom_november,
            custom_december

        FROM `tabSales Person`

        WHERE 1=1
        {conditions}

    """, filters, as_dict=1)


    data = []

    for sp in sales_persons:

        for month_no, month_name, target_field in months:

            target = sp.get(target_field) or 0

            item_condition = ""

            if filters.get("custom_main_group"):
                item_condition = " AND item.custom_main_group = %(custom_main_group)s"


            achieved = frappe.db.sql(f"""

                SELECT SUM(sii.base_net_amount)

                FROM `tabSales Invoice` si

                JOIN `tabSales Invoice Item` sii
                ON si.name = sii.parent

                JOIN `tabItem` item
                ON item.name = sii.item_code

                WHERE si.docstatus = 1
                AND MONTH(si.posting_date) = %(month)s
                AND sii.sales_person = %(sales_person)s
                {item_condition}

            """, {

                "month": month_no,
                "sales_person": sp.name,
                "custom_main_group": filters.get("custom_main_group")

            })

            achieved = achieved[0][0] or 0

            percentage = 0

            if target:
                percentage = (achieved / target) * 100


            data.append({

                "month": month_name,
                "parent_sales_person": sp.parent_sales_person,
                "region": sp.custom_region,
                "location": sp.custom_location,
                "territory": sp.custom_territory_name,
                "head_sales": sp.custom_head_sales_code,
                "target": target,
                "achieved": achieved,
                "percentage": percentage

            })

    return data