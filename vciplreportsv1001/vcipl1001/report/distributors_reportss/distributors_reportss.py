import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {
            "label": "Sales Geography",
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 380
        },
        {
            "label": "Total Invoice Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 180
        }
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    # ---------------- CHECK CUSTOM FIELDS SAFELY ----------------
    has_region = frappe.db.has_column("Sales Person", "custom_region")
    has_location = frappe.db.has_column("Sales Person", "custom_location")
    has_territory = frappe.db.has_column("Sales Person", "custom_territory")

    # ---------------- SALES PERSON MASTER ----------------
    sales_persons = frappe.db.sql(f"""
        SELECT
            name,
            parent_sales_person
            {", custom_region" if has_region else ""}
            {", custom_location" if has_location else ""}
            {", custom_territory" if has_territory else ""}
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    if not sales_persons:
        return []

    # ---------------- CUSTOMER MAPPING (TSO → CUSTOMER) ----------------
    customer_map = frappe.db.sql("""
        SELECT
            st.sales_person,
            c.name AS customer
        FROM `tabCustomer` c
        JOIN `tabSales Team` st
            ON st.parent = c.name
           AND st.parenttype = 'Customer'
    """, as_dict=True)

    tso_customers = {}
    for row in customer_map:
        tso_customers.setdefault(row.sales_person, []).append(row.customer)

    # ---------------- CUSTOMER INVOICE TOTALS ----------------
    invoice_totals = frappe.db.sql("""
        SELECT
            si.customer,
            SUM(si.base_net_total) AS amount
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        GROUP BY si.customer
    """, as_dict=True)

    customer_amount = {i.customer: flt(i.amount) for i in invoice_totals}

    # ---------------- BUILD HIERARCHY ----------------
    hierarchy = {}

    for sp in sales_persons:
        region = sp.custom_region if has_region and sp.custom_region else "No Region"
        location = sp.custom_location if has_location and sp.custom_location else "No Location"
        territory = sp.custom_territory if has_territory and sp.custom_territory else "No Territory"

        hierarchy.setdefault(region, {})
        hierarchy[region].setdefault(location, {})
        hierarchy[region][location].setdefault(territory, [])
        hierarchy[region][location][territory].append(sp.name)

    # ---------------- TREE RESULT ----------------
    result = []

    for region in hierarchy:
        result.append({
            "name": region,
            "parent": None,
            "indent": 0,
            "amount": None
        })

        for location in hierarchy[region]:
            result.append({
                "name": location,
                "parent": region,
                "indent": 1,
                "amount": None
            })

            for territory in hierarchy[region][location]:
                result.append({
                    "name": territory,
                    "parent": location,
                    "indent": 2,
                    "amount": None
                })

                for tso in hierarchy[region][location][territory]:
                    result.append({
                        "name": tso,
                        "parent": territory,
                        "indent": 3,
                        "amount": None
                    })

                    # 🔥 CUSTOMER LEVEL (NEW)
                    for customer in tso_customers.get(tso, []):
                        result.append({
                            "name": customer,
                            "parent": tso,
                            "indent": 4,
                            "amount": customer_amount.get(customer, 0)
                        })

    return result
