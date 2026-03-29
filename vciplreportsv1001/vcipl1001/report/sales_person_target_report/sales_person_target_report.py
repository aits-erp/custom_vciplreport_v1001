# import frappe
# from frappe.utils import flt


# def execute(filters=None):
#     filters = filters or {}
#     return get_columns(), get_data(filters)


# # --------------------------------------------------
# # COLUMNS
# # --------------------------------------------------
# def get_columns():
#     return [
#         {"label": "#", "fieldname": "sr_no", "fieldtype": "Int", "width": 50},

#         {
#             "label": "Sales Person",
#             "fieldname": "sales_person",
#             "fieldtype": "Link",
#             "options": "Sales Person",
#             "width": 200,
#         },

#         {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 80},
#         {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 120},

#         {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
#         {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 140},
#         {"label": "%", "fieldname": "pct", "fieldtype": "Percent", "width": 80},

#         {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 150},
#         {"label": "Total Achieved", "fieldname": "total_achieved", "fieldtype": "Currency", "width": 150},
#         {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 100},

#         # 🔥 NEW (HIDDEN DRILL COLUMN – NO UI CHANGE)
#         {"label": "Achieved Drill", "fieldname": "achieved_drill", "hidden": 1},
#     ]


# # --------------------------------------------------
# # DATA
# # --------------------------------------------------
# def get_data(filters):

#     month = int(filters.get("month"))
#     year = int(filters.get("year"))

#     # ---------- TARGETS ----------
#     targets = frappe.db.sql("""
#         SELECT
#             st.sales_person,
#             SUM(
#                 CASE %(month)s
#                     WHEN 1 THEN st.custom_january
#                     WHEN 2 THEN st.custom_february
#                     WHEN 3 THEN st.custom_march
#                     WHEN 4 THEN st.custom_april
#                     WHEN 5 THEN st.custom_may_
#                     WHEN 6 THEN st.custom_june
#                     WHEN 7 THEN st.custom_july
#                     WHEN 8 THEN st.custom_august
#                     WHEN 9 THEN st.custom_september
#                     WHEN 10 THEN st.custom_october
#                     WHEN 11 THEN st.custom_november
#                     WHEN 12 THEN st.custom_december
#                 END
#             ) AS month_target,

#             SUM(
#                 st.custom_january + st.custom_february + st.custom_march +
#                 st.custom_april + st.custom_may_ + st.custom_june +
#                 st.custom_july + st.custom_august + st.custom_september +
#                 st.custom_october + st.custom_november + st.custom_december
#             ) AS total_target

#         FROM `tabSales Team` st
#         WHERE st.parenttype = 'Customer'
#         GROUP BY st.sales_person
#     """, {"month": month}, as_dict=True)

#     # ---------- ACHIEVED (MONTH + DRILL) ----------
#     achieved_rows = frappe.db.sql("""
#         SELECT
#             st.sales_person,
#             si.name AS invoice,
#             si.posting_date,
#             si.base_net_total
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Team` st ON st.parent = si.name
#         WHERE si.docstatus = 1
#           AND MONTH(si.posting_date) = %s
#           AND YEAR(si.posting_date) = %s
#     """, (month, year), as_dict=True)

#     achieved_map = {}
#     achieved_drill = {}

#     for r in achieved_rows:
#         achieved_map.setdefault(r.sales_person, 0)
#         achieved_map[r.sales_person] += flt(r.base_net_total)

#         achieved_drill.setdefault(r.sales_person, []).append({
#             "invoice": r.invoice,
#             "date": str(r.posting_date),
#             "amount": flt(r.base_net_total),
#         })

#     # ---------- TOTAL ACHIEVED ----------
#     total_achieved = frappe.db.sql("""
#         SELECT
#             st.sales_person,
#             SUM(si.base_net_total) AS achieved
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Team` st ON st.parent = si.name
#         WHERE si.docstatus = 1
#           AND YEAR(si.posting_date) = %s
#         GROUP BY st.sales_person
#     """, year, as_dict=True)

#     total_ach_map = {a.sales_person: flt(a.achieved) for a in total_achieved}

#     # ---------- FINAL RESULT ----------
#     result = []
#     sr_no = 1

#     for t in targets:
#         role, region = get_role_and_region(t.sales_person)

#         month_target = flt(t.month_target)
#         month_ach = flt(achieved_map.get(t.sales_person))
#         month_pct = (month_ach / month_target * 100) if month_target else 0

#         tot_target = flt(t.total_target)
#         tot_ach = flt(total_ach_map.get(t.sales_person))
#         tot_pct = (tot_ach / tot_target * 100) if tot_target else 0

#         result.append({
#             "sr_no": sr_no,
#             "sales_person": t.sales_person,
#             "role": role,
#             "region": region,
#             "target": month_target,
#             "achieved": month_ach,
#             "pct": month_pct,
#             "total_target": tot_target,
#             "total_achieved": tot_ach,
#             "total_pct": tot_pct,

#             # 🔥 popup data
#             "achieved_drill": frappe.as_json(
#                 achieved_drill.get(t.sales_person, [])
#             ),
#         })

#         sr_no += 1

#     return result


# def get_role_and_region(sp):
#     parent = frappe.db.get_value("Sales Person", sp, "parent_sales_person")
#     if not parent:
#         return "RSM", sp
#     if parent.lower().startswith("rsm"):
#         return "ASM", parent
#     if parent.lower().startswith("asm"):
#         rsm = frappe.db.get_value("Sales Person", parent, "parent_sales_person")
#         return "TSO", rsm or parent
#     return "TSO", parent

import frappe
from frappe.utils import flt, nowdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
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

        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 140},
        {"label": "%", "fieldname": "pct", "fieldtype": "Percent", "width": 80},

        {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 150},
        {"label": "Total Achieved", "fieldname": "total_achieved", "fieldtype": "Currency", "width": 150},
        {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 100},

        {"label": "Achieved Drill", "fieldname": "achieved_drill", "hidden": 1},
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    # ✅ SAFE DEFAULTS (THIS FIXES YOUR ERROR)
    today = nowdate()
    month = int(filters.get("month") or today[5:7])
    year = int(filters.get("year") or today[:4])

    # ---------- TARGETS ----------
    targets = frappe.db.sql("""
        SELECT
            st.sales_person,

            SUM(
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
                END
            ) AS month_target,

            SUM(
                st.custom_january + st.custom_february + st.custom_march +
                st.custom_april + st.custom_may_ + st.custom_june +
                st.custom_july + st.custom_august + st.custom_september +
                st.custom_october + st.custom_november + st.custom_december
            ) AS total_target

        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
        GROUP BY st.sales_person
    """, {"month": month}, as_dict=True)

    target_map = {t.sales_person: t for t in targets}

    # ---------- ACHIEVED (MONTH + DRILL) ----------
    achieved_rows = frappe.db.sql("""
        SELECT
            st.sales_person,
            si.name AS invoice,
            si.posting_date,
            si.base_net_total
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
          AND MONTH(si.posting_date) = %s
          AND YEAR(si.posting_date) = %s
    """, (month, year), as_dict=True)

    achieved_map = {}
    achieved_drill = {}

    for r in achieved_rows:
        achieved_map.setdefault(r.sales_person, 0)
        achieved_map[r.sales_person] += flt(r.base_net_total)

        achieved_drill.setdefault(r.sales_person, []).append({
            "invoice": r.invoice,
            "date": str(r.posting_date),
            "amount": flt(r.base_net_total),
        })

    # ---------- TOTAL ACHIEVED ----------
    total_achieved = frappe.db.sql("""
        SELECT
            st.sales_person,
            SUM(si.base_net_total) AS achieved
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
          AND YEAR(si.posting_date) = %s
        GROUP BY st.sales_person
    """, year, as_dict=True)

    total_ach_map = {a.sales_person: flt(a.achieved) for a in total_achieved}

    # ---------- FINAL RESULT ----------
    result = []
    sr_no = 1

    for sp, t in target_map.items():
        role, region = get_role_and_region(sp)

        month_target = flt(t.month_target)
        month_ach = flt(achieved_map.get(sp))
        month_pct = (month_ach / month_target * 100) if month_target else 0

        tot_target = flt(t.total_target)
        tot_ach = flt(total_ach_map.get(sp))
        tot_pct = (tot_ach / tot_target * 100) if tot_target else 0

        result.append({
            "sr_no": sr_no,
            "sales_person": sp,
            "role": role,
            "region": region,
            "target": month_target,
            "achieved": month_ach,
            "pct": month_pct,
            "total_target": tot_target,
            "total_achieved": tot_ach,
            "total_pct": tot_pct,
            "achieved_drill": frappe.as_json(achieved_drill.get(sp, [])),
        })

        sr_no += 1

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
