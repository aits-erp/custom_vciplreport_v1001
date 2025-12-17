import frappe
from frappe.utils import flt


def execute(filters=None):
    return get_columns(), get_data(filters or {})


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    cols = [
        {"label": "#", "fieldname": "sr_no", "fieldtype": "Int", "width": 50},
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200,
        },
        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 80},
        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 120},
    ]

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in months:
        cols.append({"label": f"{m} Target", "fieldname": f"{m.lower()}_target", "fieldtype": "Currency", "width": 120})
        cols.append({"label": f"{m} Ach", "fieldname": f"{m.lower()}_ach", "fieldtype": "Currency", "width": 120})
        cols.append({"label": f"{m} %", "fieldname": f"{m.lower()}_pct", "fieldtype": "Percent", "width": 90})

    cols.extend([
        {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 140},
        {"label": "Total Ach", "fieldname": "total_ach", "fieldtype": "Currency", "width": 140},
        {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 100},
    ])

    return cols


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    # 🔹 Aggregate TARGETS per Sales Person
    targets = frappe.db.sql("""
        SELECT
            st.sales_person,
            SUM(st.custom_january)   AS jan,
            SUM(st.custom_february)  AS feb,
            SUM(st.custom_march)     AS mar,
            SUM(st.custom_april)     AS apr,
            SUM(st.custom_may_)      AS may,
            SUM(st.custom_june)      AS jun,
            SUM(st.custom_july)      AS jul,
            SUM(st.custom_august)    AS aug,
            SUM(st.custom_september) AS sep,
            SUM(st.custom_october)   AS oct,
            SUM(st.custom_november)  AS nov,
            SUM(st.custom_december)  AS dec_val
        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
        GROUP BY st.sales_person
    """, as_dict=True)

    # 🔹 Aggregate ACHIEVEMENTS per Sales Person
    invoices = frappe.db.sql("""
        SELECT
            st.sales_person,
            MONTH(si.posting_date) AS month,
            SUM(si.base_net_total) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
        GROUP BY st.sales_person, MONTH(si.posting_date)
    """, as_dict=True)

    ach_map = {}
    for r in invoices:
        ach_map.setdefault(r.sales_person, {})[r.month] = flt(r.amount)

    result = []
    sr_no = 1

    for t in targets:
        role, region = get_role_and_region(t.sales_person)

        row = {
            "sr_no": sr_no,
            "sales_person": t.sales_person,
            "role": role,
            "region": region,
        }
        sr_no += 1

        total_target = 0
        total_ach = 0

        month_targets = {
            1: t.jan, 2: t.feb, 3: t.mar, 4: t.apr, 5: t.may, 6: t.jun,
            7: t.jul, 8: t.aug, 9: t.sep, 10: t.oct, 11: t.nov, 12: t.dec_val
        }

        for m_no, m_key in zip(
            range(1, 13),
            ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
        ):
            target = flt(month_targets.get(m_no))
            ach = flt(ach_map.get(t.sales_person, {}).get(m_no))
            pct = (ach / target * 100) if target else 0

            row[f"{m_key}_target"] = target
            row[f"{m_key}_ach"] = ach
            row[f"{m_key}_pct"] = pct

            total_target += target
            total_ach += ach

        row["total_target"] = total_target
        row["total_ach"] = total_ach
        row["total_pct"] = (total_ach / total_target * 100) if total_target else 0

        result.append(row)

    return result


def get_role_and_region(sp):
    parent = frappe.db.get_value("Sales Person", sp, "parent_sales_person")
    if not parent:
        return "RSM", sp
    if parent.lower().startswith("rsm"):
        return "ASM", parent
    if parent.lower().startswith("asm"):
        rsm = frappe.db.get_value("Sales Person", parent, "parent_sales_person")
        return "TSO", rsm or parent
    return "TSO", parent
