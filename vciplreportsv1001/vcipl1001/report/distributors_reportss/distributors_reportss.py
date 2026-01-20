import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = []

    parent_sp = filters.get("parent_sales_person")

    # --------------------------------------------------
    # LEVEL 0 : Parent Sales Person (optional)
    # --------------------------------------------------
    if parent_sp:
        data.append({
            "name": parent_sp,
            "amount": get_sales_person_amount(parent_sp),
            "indent": 0
        })

    # --------------------------------------------------
    # LEVEL 1 : Geography (Territory root)
    # --------------------------------------------------
    geographies = frappe.get_all(
        "Territory",
        filters={"parent_territory": None},
        fields=["name"]
    )

    for geo in geographies:
        data.append({
            "name": geo.name,
            "amount": get_territory_amount(geo.name),
            "indent": 1 if parent_sp else 0
        })

        # --------------------------------------------------
        # LEVEL 2 : Location
        # --------------------------------------------------
        locations = frappe.get_all(
            "Territory",
            filters={"parent_territory": geo.name},
            fields=["name"]
        )

        for loc in locations:
            data.append({
                "name": loc.name,
                "amount": get_territory_amount(loc.name),
                "indent": 2 if parent_sp else 1
            })

            # --------------------------------------------------
            # LEVEL 3 : Sales Person
            # --------------------------------------------------
            sales_persons = frappe.get_all(
                "Sales Person",
                filters={"territory": loc.name},
                fields=["name"]
            )

            for sp in sales_persons:
                # If parent selected, show only its hierarchy
                if parent_sp and not is_child_of(sp.name, parent_sp):
                    continue

                data.append({
                    "name": sp.name,
                    "amount": get_sales_person_amount(sp.name),
                    "indent": 3 if parent_sp else 2
                })

                # --------------------------------------------------
                # LEVEL 4 : Customers
                # --------------------------------------------------
                customers = frappe.db.sql("""
                    SELECT DISTINCT c.name
                    FROM `tabCustomer` c
                    JOIN `tabSales Team` st ON st.parent = c.name
                    WHERE st.sales_person = %s
                """, sp.name, as_dict=True)

                for cust in customers:
                    data.append({
                        "name": cust.name,
                        "amount": get_customer_amount(cust.name),
                        "indent": 4 if parent_sp else 3
                    })

    return columns, data


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def is_child_of(sales_person, parent):
    return frappe.db.exists(
        "Sales Person",
        {
            "name": sales_person,
            "parent_sales_person": parent
        }
    )


def get_columns():
    return [
        {
            "label": "Sales Hierarchy",
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
