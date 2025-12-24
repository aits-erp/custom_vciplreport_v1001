import frappe
from frappe.utils import flt, getdate


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

    months = [
        ("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4),
        ("May", 5), ("Jun", 6), ("Jul", 7), ("Aug", 8),
        ("Sep", 9), ("Oct", 10), ("Nov", 11), ("Dec", 12)
    ]

    for m, _ in months:
        cols.append({"label": f"{m} Target", "fieldname": f"{m.lower()}_target", "fieldtype": "Currency", "width": 120})
        cols.append({"label": f"{m} Achieved", "fieldname": f"{m.lower()}_achieved", "fieldtype": "Currency", "width": 120, "hidden": 1})
        cols.append({"label": f"{m} %", "fieldname": f"{m.lower()}_pct", "fieldtype": "Percent", "width": 90, "hidden": 1})

        # hidden drill helpers
        cols.append({"label": f"{m} Ach Drill", "fieldname": f"{m.lower()}_ach_drill", "hidden": 1})

    cols.extend([
        {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 150},
        {"label": "Total Achieved", "fieldname": "total_achieved", "fieldtype": "Currency", "width": 150, "hidden": 1},
        {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 120, "hidden": 1},
        {"label": "Total Ach Drill", "fieldname": "total_ach_drill", "hidden": 1},
    ])

    return cols


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    # ---------------- TARGETS ----------------
    targets = frappe.db.sql("""
        SELECT
            c.name AS customer,
            st.sales_person,

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
            st.custom_december  AS dec_val

        FROM `tabCustomer` c
        JOIN `tabSales Team` st
            ON st.parent = c.name
           AND st.parenttype = 'Customer'
        WHERE c.disabled = 0
    """, as_dict=True)

    # ---------------- ACHIEVEMENTS ----------------
    invoices = frappe.db.sql("""
        SELECT
            si.name,
            si.customer,
            st.sales_person,
            MONTH(si.posting_date) AS month,
            si.posting_date,
            si.base_net_total
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
    """, as_dict=True)

    ach_map = {}
    for i in invoices:
        key = (i.customer, i.sales_person, i.month)
        ach_map.setdefault(key, []).append({
            "invoice": i.name,
            "date": str(i.posting_date),
            "amount": i.base_net_total
        })

    result = []

    for t in targets:
        row = {
            "customer": t.customer,
            "sales_person": t.sales_person,
            "role": get_role(t.sales_person),
        }

        month_targets = {
            1: t.jan, 2: t.feb, 3: t.mar, 4: t.apr, 5: t.may, 6: t.jun,
            7: t.jul, 8: t.aug, 9: t.sep, 10: t.oct, 11: t.nov, 12: t.dec_val
        }

        total_target = 0
        total_ach = 0
        total_drill = []

        for m_no, m_key in zip(
            range(1, 13),
            ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
        ):
            target = flt(month_targets.get(m_no))
            drills = ach_map.get((t.customer, t.sales_person, m_no), [])
            ach = sum(d["amount"] for d in drills)
            pct = (ach / target * 100) if target else 0

            row[f"{m_key}_target"] = target
            row[f"{m_key}_achieved"] = ach
            row[f"{m_key}_pct"] = pct
            row[f"{m_key}_ach_drill"] = frappe.as_json(drills)

            total_target += target
            total_ach += ach
            total_drill.extend(drills)

        row["total_target"] = total_target
        row["total_achieved"] = total_ach
        row["total_pct"] = (total_ach / total_target * 100) if total_target else 0
        row["total_ach_drill"] = frappe.as_json(total_drill)

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
