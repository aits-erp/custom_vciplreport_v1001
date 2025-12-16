import frappe
from frappe.utils import flt


def execute(filters=None):
    return get_columns(), get_data(filters or {})


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    cols = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 220},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 80},
    ]

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in months:
        cols.append({"label": f"{m} Target", "fieldname": f"{m.lower()}_target", "fieldtype": "Currency", "width": 120})
        cols.append({"label": f"{m} Ach", "fieldname": f"{m.lower()}_ach", "fieldtype": "Currency", "width": 120})
        cols.append({"label": f"{m} %", "fieldname": f"{m.lower()}_pct", "fieldtype": "Percent", "width": 90})

    cols.extend([
        {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 150},
        {"label": "Total Ach", "fieldname": "total_ach", "fieldtype": "Currency", "width": 150},
        {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 120},
        {"label": "ach_drill", "fieldname": "ach_drill", "hidden": 1},  # for click
    ])

    return cols


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    targets = frappe.db.sql("""
        SELECT
            c.name AS customer,
            st.sales_person,
            st.allocated_percentage,

            st.custom_january   AS jan,
            st.custom_february  AS feb,
            st.custom_march     AS mar,
            st.custom_april     AS apr,
            st.custom_may_      AS may,
            st.custom_june      AS jun,
            st.custom_july      AS jul,
            st.custom_august    AS aug,
            st.custom_september AS sep,
            st.custom_october   AS oct,
            st.custom_november  AS nov,
            st.custom_december  AS dec
        FROM `tabCustomer` c
        JOIN `tabSales Team` st
            ON st.parent = c.name
           AND st.parenttype = 'Customer'
        WHERE c.disabled = 0
    """, as_dict=True)

    # ---- Achievement (Invoices)
    invoices = frappe.db.sql("""
        SELECT
            si.customer,
            st.sales_person,
            MONTH(si.posting_date) AS month,
            SUM(si.base_net_total) AS amount,
            GROUP_CONCAT(si.name) AS invoices
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
        GROUP BY si.customer, st.sales_person, MONTH(si.posting_date)
    """, as_dict=True)

    ach_map = {}
    for r in invoices:
        ach_map.setdefault((r.customer, r.sales_person), {})[r.month] = {
            "amount": flt(r.amount),
            "invoices": r.invoices
        }

    result = []

    for t in targets:
        row = {
            "customer": t.customer,
            "sales_person": t.sales_person,
            "role": get_role(t.sales_person),
        }

        total_target = 0
        total_ach = 0
        drill = {}

        month_map = {
            1: t.jan, 2: t.feb, 3: t.mar, 4: t.apr, 5: t.may, 6: t.jun,
            7: t.jul, 8: t.aug, 9: t.sep, 10: t.oct, 11: t.nov, 12: t.dec
        }

        for m_no, m_key in zip(range(1,13),
                               ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]):

            target = flt(month_map.get(m_no))
            ach = flt(ach_map.get((t.customer, t.sales_person), {}).get(m_no, {}).get("amount"))
            pct = (ach / target * 100) if target else 0

            row[f"{m_key}_target"] = target
            row[f"{m_key}_ach"] = ach
            row[f"{m_key}_pct"] = pct

            total_target += target
            total_ach += ach

            if ach:
                drill[m_key] = ach_map[(t.customer, t.sales_person)][m_no]["invoices"]

        row["total_target"] = total_target
        row["total_ach"] = total_ach
        row["total_pct"] = (total_ach / total_target * 100) if total_target else 0
        row["ach_drill"] = frappe.as_json(drill)

        result.append(row)

    return result


def get_role(sp):
    parent = frappe.db.get_value("Sales Person", sp, "parent_sales_person")
    if not parent:
        return "RSM"
    if parent.lower().startswith("rsm"):
        return "ASM"
    if parent.lower().startswith("asm"):
        return "TSO"
    return "TSO"
