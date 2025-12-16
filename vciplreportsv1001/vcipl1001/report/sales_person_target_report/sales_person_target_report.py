import frappe


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 220,
        },
        {
            "label": "Parent Sales Person",
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 220,
        },
        {
            "label": "Contribution (%)",
            "fieldname": "allocated_percentage",
            "fieldtype": "Float",
            "width": 130,
        },

        {"label": "January", "fieldname": "custom_january", "fieldtype": "Data", "width": 120},
        {"label": "February", "fieldname": "custom_february", "fieldtype": "Data", "width": 120},
        {"label": "March", "fieldname": "custom_march", "fieldtype": "Data", "width": 120},
        {"label": "April", "fieldname": "custom_april", "fieldtype": "Data", "width": 120},
        {"label": "May", "fieldname": "custom_may_", "fieldtype": "Data", "width": 120},
        {"label": "June", "fieldname": "custom_june", "fieldtype": "Data", "width": 120},
        {"label": "July", "fieldname": "custom_july", "fieldtype": "Data", "width": 120},
        {"label": "August", "fieldname": "custom_august", "fieldtype": "Data", "width": 120},
        {"label": "September", "fieldname": "custom_september", "fieldtype": "Data", "width": 120},
        {"label": "October", "fieldname": "custom_october", "fieldtype": "Data", "width": 120},
        {"label": "November", "fieldname": "custom_november", "fieldtype": "Data", "width": 120},
        {"label": "December", "fieldname": "custom_december", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    conditions = ""
    if filters.get("sales_person"):
        conditions = " AND sp.name = %(sales_person)s"

    query = f"""
        SELECT
            sp.name AS sales_person,
            sp.parent_sales_person AS parent_sales_person,
            st.allocated_percentage AS allocated_percentage,

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
            st.custom_december

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
