import frappe

def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [

        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 120},

        {"label": "Parent Sales Person", "fieldname": "parent_sales_person", "fieldtype": "Data", "width": 200},

        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 150},

        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 150},

        {"label": "Territory", "fieldname": "territory", "fieldtype": "Data", "width": 200},

        {"label": "Head Sales Code", "fieldname": "head_sales", "fieldtype": "Data", "width": 150},

        {"label": "Target", "fieldname": "target", "fieldtype": "Float", "width": 120},

        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Float", "width": 120},

        {"label": "Achieved %", "fieldname": "percentage", "fieldtype": "Percent", "width": 120},

    ]


def get_data(filters):

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
            custom_head_sales_code

        FROM `tabSales Person`

        WHERE 1=1
        {conditions}

    """, filters, as_dict=1)

    data = []

    for sp in sales_persons:

        data.append({

            "month": "",
            "parent_sales_person": sp.parent_sales_person,
            "region": sp.custom_region,
            "location": sp.custom_location,
            "territory": sp.custom_territory_name,
            "head_sales": sp.custom_head_sales_code,
            "target": 0,
            "achieved": 0,
            "percentage": 0

        })

    return data