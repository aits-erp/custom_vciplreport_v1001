import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "Main Group", "fieldname": "custom_main_group", "fieldtype": "Data", "width": 160},
        {"label": "Sub Group", "fieldname": "sub_group", "fieldtype": "Data", "width": 140},
        {"label": "Sub Group 1", "fieldname": "sub_group1", "fieldtype": "Data", "width": 140},
        {"label": "Custom Sub Group 1", "fieldname": "custom_sub_group1", "fieldtype": "Data", "width": 160},
        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 120},
        {"label": "Custom Sub Group", "fieldname": "custom_sub_group", "fieldtype": "Data", "width": 160},
        {"label": "Sales Amount", "fieldname": "sales_amount", "fieldtype": "Currency", "width": 140},
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):
    month = int(filters.get("month"))
    year = int(filters.get("year"))
    company = filters.get("company")

    return frappe.db.sql("""
        SELECT
            sii.custom_main_group AS custom_main_group,
            sii.item_group AS sub_group,
            sii.custom_sub_group1 AS sub_group1,
            sii.custom_sub_group1 AS custom_sub_group1,

            c.territory AS region,
            c.custom_sub_group AS custom_sub_group,

            SUM(sii.base_net_amount) AS sales_amount

        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabCustomer` c ON c.name = si.customer

        WHERE si.docstatus = 1
          AND si.company = %(company)s
          AND MONTH(si.posting_date) = %(month)s
          AND YEAR(si.posting_date) = %(year)s

        GROUP BY
            sii.custom_main_group,
            sii.item_group,
            sii.custom_sub_group1,
            c.territory,
            c.custom_sub_group

        ORDER BY
            sii.custom_main_group,
            sii.item_group
    """, {
        "company": company,
        "month": month,
        "year": year
    }, as_dict=True)
