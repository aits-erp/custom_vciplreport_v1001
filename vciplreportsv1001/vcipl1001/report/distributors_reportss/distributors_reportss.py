import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


# --------------------------------------------------
# COLUMNS (TREE USES ONLY ONE NAME COLUMN)
# --------------------------------------------------
def get_columns():
    return [
        {
            "label": "Sales Geography",
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


# --------------------------------------------------
# MAIN DATA
# --------------------------------------------------
def get_data(filters):

    result = []

    # ---------------- SALES PERSON MASTER ----------------
    sales_persons = frappe.db.sql("""
        SELECT
            name,
            parent_sales_person,
            custom_region,
            custom_location,
            custom_territory
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    if not sales_persons:
        return []

    # ---------------- INVOICE TOTALS (TSO LEVEL) ----------------
    invoice_totals = frappe.db.sql("""
        SELECT
            st.sales_person,
            SUM(si.base_net_total) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
        GROUP BY st.sales_person
    """, as_dict=True)

    amount_map = {i.sales_person: flt(i.amount) for i in invoice_totals}

    # ---------------- BUILD HIERARCHY MAP ----------------
    hierarchy = {}

    for sp in sales_persons:
        region = sp.custom_region or "Undefined Region"
        location = sp.custom_location or "Undefined Location"
        territory = sp.custom_territory or "Undefined Territory"

        hierarchy.setdefault(region, {})
        hierarchy[region].setdefault(location, {})
        hierarchy[region][location].setdefault(territory, [])
        hierarchy[region][location][territory].append(sp.name)

    # ---------------- TREE BUILDING ----------------
    for region in hierarchy:
        region_id = f"REGION::{region}"
        result.append({
            "name": region,
            "parent": None,
            "indent": 0,
            "amount": None
        })

        for location in hierarchy[region]:
            location_id = f"{region_id}::LOC::{location}"
            result.append({
                "name": location,
                "parent": region,
                "indent": 1,
                "amount": None
            })

            for territory in hierarchy[region][location]:
                territory_id = f"{location_id}::TER::{territory}"
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
                        "amount": amount_map.get(tso, 0)
                    })

    return result
