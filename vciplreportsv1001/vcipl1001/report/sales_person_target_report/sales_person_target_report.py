import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": "Parent Sales Person",
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": "Contribution (%)",
            "fieldname": "allocated_percentage",
            "fieldtype": "Float",
            "width": 130
        },

        {"label": "January", "fieldname": "january", "fieldtype": "Currency", "width": 140},
        {"label": "February", "fieldname": "february", "fieldtype": "Currency", "width": 140},
        {"label": "March", "fieldname": "march", "fieldtype": "Currency", "width": 140},
        {"label": "April", "fieldname": "april", "fieldtype": "Currency", "width": 140},
        {"label": "May", "fieldname": "may", "fieldtype": "Currency", "width": 140},
        {"label": "June", "fieldname": "june", "fieldtype": "Currency", "width": 140},
        {"label": "July", "fieldname": "july", "fieldtype": "Currency", "width": 140},
        {"label": "August", "fieldname": "august", "fieldtype": "Currency", "width": 140},
        {"label": "September", "fieldname": "september", "fieldtype": "Currency", "width": 140},
        {"label": "October", "fieldname": "october", "fieldtype": "Currency", "width": 140},
        {"label": "November", "fieldname": "november", "fieldtype": "Currency", "width": 140},
        {"label": "December", "fieldname": "december", "fieldtype": "Currency", "width": 140},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("sales_person"):
        conditions += " AND sp.name = %(sales_person)s"

    query = f"""
        SELECT
            sp.name AS sales_person,
            sp.parent_sales_person AS parent_sales_person,
            st.allocated_percentage AS allocated_percentage,

            st.custom_january AS january,
            st.custom_february AS february,
            st.custom_march AS march,
            st.custom_april AS april,
            st.custom_may AS may,
            st.custom_june AS june,
            st.custom_july AS july,
            st.custom_august AS august,
            st.custom_september AS september,
            st.custom_october AS october,
            st.custom_november AS november,
            st.custom_december AS december

        FROM
            `tabSales Person` sp
        LEFT JOIN
            `tabSales Team` st
                ON st.sales_person = sp.name

        WHERE
            sp.disabled = 0
            {conditions}

        ORDER BY
            sp.lft
    """

    return frappe.db.sql(query, filters, as_dict=True)
