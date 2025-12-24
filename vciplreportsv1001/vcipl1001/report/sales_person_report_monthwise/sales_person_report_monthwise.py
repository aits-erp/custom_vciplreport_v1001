import frappe
from frappe.utils import flt, getdate


def execute(filters=None):
    return get_columns(), get_data(filters or {})


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "#", "fieldname": "idx", "width": 50},
        {"label": "Main Group", "fieldname": "main_group", "width": 150},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Role", "fieldname": "role", "width": 80},
        {"label": "Region", "fieldname": "region", "width": 120},

        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 140},
        {"label": "%", "fieldname": "percentage", "fieldtype": "Percent", "width": 90},

        {"label": "Ach Drill", "fieldname": "ach_drill", "hidden": 1},
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    year = int(filters.get("year"))
    month = int(filters.get("month"))

    # Map month → field name
    month_field = {
        1: "custom_january",
        2: "custom_february",
        3: "custom_march",
        4: "custom_april",
        5: "custom_may_",
        6: "custom_june",
        7: "custom_july",
        8: "custom_august",
        9: "custom_september",
        10: "custom_october",
        11: "custom_november",
        12: "custom_december",
    }[month]

    # --------------------------------------------------
    # TARGETS (FROM CUSTOMER → SALES TEAM)
    # --------------------------------------------------
    targets = frappe.db.sql(f"""
        SELECT
            c.customer_group AS main_group,
            c.name AS customer,
            st.sales_person,
            sp.custom_role AS role,
            sp.custom_region AS region,
            st.{month_field} AS target
        FROM `tabCustomer` c
        JOIN `tabSales Team` st
            ON st.parent = c.name
           AND st.parenttype = 'Customer'
        JOIN `tabSales Person` sp
            ON sp.name = st.sales_person
        WHERE c.disabled = 0
    """, as_dict=True)

    # --------------------------------------------------
    # ACHIEVEMENT (SALES INVOICE + ALLOCATION)
    # --------------------------------------------------
    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer,
            si.posting_date,
            si.base_net_total,
            st.sales_person,
            st.allocated_percentage
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st
            ON st.parent = si.name
        WHERE si.docstatus = 1
          AND YEAR(si.posting_date) = %(year)s
          AND MONTH(si.posting_date) = %(month)s
    """, {"year": year, "month": month}, as_dict=True)

    ach_map = {}

    for inv in invoices:
        key = (inv.customer, inv.sales_person)
        amt = flt(inv.base_net_total) * flt(inv.allocated_percentage) / 100

        ach_map.setdefault(key, {
            "amount": 0,
            "drill": []
        })

        ach_map[key]["amount"] += amt
        ach_map[key]["drill"].append({
            "invoice": inv.invoice,
            "date": str(inv.posting_date),
            "amount": amt
        })

    # --------------------------------------------------
    # FINAL MERGE
    # --------------------------------------------------
    result = []
    idx = 1

    for t in targets:
        key = (t.customer, t.sales_person)
        achieved = ach_map.get(key, {}).get("amount", 0)
        drill = ach_map.get(key, {}).get("drill", [])

        target = flt(t.target)
        pct = (achieved / target * 100) if target else 0

        result.append({
            "idx": idx,
            "main_group": t.main_group,
            "customer": t.customer,
            "sales_person": t.sales_person,
            "role": t.role,
            "region": t.region,
            "target": target,
            "achieved": achieved,
            "percentage": pct,
            "ach_drill": frappe.as_json(drill)
        })

        idx += 1

    return result
