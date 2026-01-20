import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    data = []
    columns = get_columns()

    parent_sales_person = filters.get("parent_sales_person")
    root_territory = filters.get("custom_territory")

    if not parent_sales_person or not root_territory:
        return columns, data

    # -------------------------------------------------
    # LEVEL 0 : Parent Sales Person
    # -------------------------------------------------
    data.append({
        "name": parent_sales_person,
        "amount": get_sales_person_amount(parent_sales_person),
        "indent": 0
    })

    # -------------------------------------------------
    # LEVEL 1 : Territory (West)
    # -------------------------------------------------
    data.append({
        "name": root_territory,
        "amount": get_territory_amount(root_territory),
        "indent": 1
    })

    # -------------------------------------------------
    # LEVEL 2 : Sub Territories (Mumbai)
    # -------------------------------------------------
    sub_territories = frappe.get_all(
        "Territory",
        filters={"parent_territory": root_territory},
        fields=["name"]
    )

    for sub in sub_territories:
        data.append({
            "name": sub.name,
            "amount": get_territory_amount(sub.name),
            "indent": 2
        })

        # -------------------------------------------------
        # LEVEL 3 : Customers (C0047)
        # -------------------------------------------------
        customers = frappe.get_all(
            "Customer",
            filters={"territory": sub.name},
            fields=["name"]
        )

        for cust in customers:
            data.append({
                "name": cust.name,
                "amount": get_customer_amount(cust.name),
                "indent": 3
            })

            # -------------------------------------------------
            # LEVEL 4 : Sales Person (Ashish Masre)
            # -------------------------------------------------
            sales_persons = frappe.db.sql("""
                SELECT DISTINCT st.sales_person
                FROM `tabSales Team` st
                WHERE st.parenttype = 'Customer'
                  AND st.parent = %s
            """, cust.name, as_dict=True)

            for sp in sales_persons:
                data.append({
                    "name": sp.sales_person,
                    "amount": get_sales_person_amount(sp.sales_person),
                    "indent": 4
                })

    return columns, data


# -------------------------------------------------
# COLUMNS
# -------------------------------------------------
def get_columns():
    return [
        {
            "label": "Distributor Hierarchy",
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 350
        },
        {
            "label": "Total Invoice Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 180
        }
    ]


# -------------------------------------------------
# AMOUNT HELPERS
# -------------------------------------------------
def get_customer_amount(customer):
    return flt(frappe.db.sql("""
        SELECT SUM(base_grand_total)
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, customer)[0][0])


def get_sales_person_amount(sales_person):
    return flt(frappe.db.sql("""
        SELECT SUM(si.base_grand_total)
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE st.sales_person = %s AND si.docstatus = 1
    """, sales_person)[0][0])


def get_territory_amount(territory):
    return flt(frappe.db.sql("""
        SELECT SUM(base_grand_total)
        FROM `tabSales Invoice`
        WHERE territory = %s AND docstatus = 1
    """, territory)[0][0])
