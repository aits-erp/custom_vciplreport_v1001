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
            "width": 360
        },
        {
            "label": "Target",
            "fieldname": "target",
            "fieldtype": "Currency",
            "width": 160
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

    month = int(filters.get("month") or frappe.utils.nowdate()[5:7])

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

    # ---------------- CUSTOMER ↔ TSO MAP ----------------
    customer_map = frappe.db.sql("""
        SELECT
            st.sales_person,
            st.parent AS customer,

            CASE %(month)s
                WHEN 1 THEN st.custom_january
                WHEN 2 THEN st.custom_february
                WHEN 3 THEN st.custom_march
                WHEN 4 THEN st.custom_april
                WHEN 5 THEN st.custom_may_
                WHEN 6 THEN st.custom_june
                WHEN 7 THEN st.custom_july
                WHEN 8 THEN st.custom_august
                WHEN 9 THEN st.custom_september
                WHEN 10 THEN st.custom_october
                WHEN 11 THEN st.custom_november
                WHEN 12 THEN st.custom_december
            END AS target

        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
    """, {"month": month}, as_dict=True)

    tso_customers = {}
    customer_target = {}

    for r in customer_map:
        tso_customers.setdefault(r.sales_person, []).append(r.customer)
        customer_target[r.customer] = flt(r.target)

    # ---------------- CUSTOMER INVOICE TOTALS ----------------
    invoice_totals = frappe.db.sql("""
        SELECT
            customer,
            SUM(base_net_total) AS amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        GROUP BY customer
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
            "target": None,
            "amount": None
        })

        for location in hierarchy[region]:
            result.append({
                "name": location,
                "parent": region,
                "indent": 1,
                "target": None,
                "amount": None
            })

            for territory in hierarchy[region][location]:
                result.append({
                    "name": territory,
                    "parent": location,
                    "indent": 2,
                    "target": None,
                    "amount": None
                })

                for tso in hierarchy[region][location][territory]:
                    result.append({
                        "name": tso,
                        "parent": territory,
                        "indent": 3,
                        "target": None,
                        "amount": None
                    })

                    # 🔥 CUSTOMER LEVEL
                    for customer in tso_customers.get(tso, []):
                        result.append({
                            "name": customer,
                            "parent": tso,
                            "indent": 4,
                            "target": customer_target.get(customer, 0),
                            "amount": customer_amount.get(customer, 0)
                        })

    return result
