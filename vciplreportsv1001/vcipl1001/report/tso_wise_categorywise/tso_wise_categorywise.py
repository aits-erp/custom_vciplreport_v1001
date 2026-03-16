import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [
        {
            "label": "Month",
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": "TSO",
            "fieldname": "tso",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 220
        },
        {
            "label": "Target",
            "fieldname": "target",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Achieved Amount",
            "fieldname": "achieved",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": "Achieved %",
            "fieldname": "achieved_percent",
            "fieldtype": "Percent",
            "width": 120
        }
    ]


def get_data(filters):

    month_map = {
        "JAN": ("custom_january", 1),
        "FEB": ("custom_february", 2),
        "MAR": ("custom_march", 3),
        "APR": ("custom_april", 4),
        "MAY": ("custom_may_", 5),
        "JUN": ("custom_june", 6),
        "JUL": ("custom_july", 7),
        "AUG": ("custom_august", 8),
        "SEP": ("custom_september", 9),
        "OCT": ("custom_october", 10),
        "NOV": ("custom_november", 11),
        "DEC": ("custom_december", 12)
    }

    data = []

    # Get TSO under selected Sales Head
    sales_persons = frappe.db.sql(
        """
        SELECT name, custom_territory
        FROM `tabSales Person`
        WHERE parent_sales_person = %(parent_sales_person)s
        """,
        filters,
        as_dict=1
    )

    for sp in sales_persons:

        # Get customers assigned to TSO
        customers = frappe.db.sql(
            """
            SELECT
                parent as customer,
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
            FROM `tabCustomer Sales Person`
            WHERE sales_person = %s
            """,
            sp.name,
            as_dict=1
        )

        for cust in customers:

            for month, (field, month_no) in month_map.items():

                target = cust.get(field) or 0

                # Achieved amount from Sales Invoice
                achieved = frappe.db.sql(
                    """
                    SELECT SUM(base_net_total)
                    FROM `tabSales Invoice`
                    WHERE customer = %s
                    AND docstatus = 1
                    AND MONTH(posting_date) = %s
                    """,
                    (cust.customer, month_no)
                )[0][0] or 0

                percent = 0
                if target:
                    percent = (achieved / target) * 100

                data.append({
                    "month": month,
                    "tso": sp.custom_territory,
                    "customer": cust.customer,
                    "target": target,
                    "achieved": achieved,
                    "achieved_percent": percent
                })

    return data