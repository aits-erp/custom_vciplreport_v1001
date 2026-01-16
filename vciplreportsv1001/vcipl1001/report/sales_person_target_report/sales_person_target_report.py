# import frappe
from frappe.utils import today, getdate, flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "Distributor", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 220},
        {"label": "RSM", "fieldname": "rsm", "fieldtype": "Link", "options": "Sales Person", "width": 140},
        {"label": "ASM", "fieldname": "asm", "fieldtype": "Link", "options": "Sales Person", "width": 140},
        {"label": "TSO", "fieldname": "tso", "fieldtype": "Link", "options": "Sales Person", "width": 140},

        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 120},
        {"label": "Territory", "fieldname": "territory", "fieldtype": "Data", "width": 120},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 120},

        {"label": "Month Target", "fieldname": "month_target", "fieldtype": "Currency", "width": 140},
        {"label": "Month Achieved", "fieldname": "month_achieved", "fieldtype": "Currency", "width": 140},
        {"label": "Month %", "fieldname": "month_pct", "fieldtype": "Percent", "width": 90},

        {"label": "YTD Target", "fieldname": "ytd_target", "fieldtype": "Currency", "width": 140},
        {"label": "YTD Achieved", "fieldname": "ytd_achieved", "fieldtype": "Currency", "width": 140},
        {"label": "YTD %", "fieldname": "ytd_pct", "fieldtype": "Percent", "width": 90},

        {"label": "Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 140},
        {"label": "Overdue", "fieldname": "overdue", "fieldtype": "Currency", "width": 140},

        # hidden drill
        {"label": "Achieved Drill", "fieldname": "achieved_drill", "hidden": 1},
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    # ---------------- SALES PERSON MASTER ----------------
    sales_persons = frappe.db.sql("""
        SELECT
            name,
            parent_sales_person,
            custom_region,
            custom_territory,
            custom_location
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    sp_map = {sp.name: sp for sp in sales_persons}

    # ---------------- CUSTOMER + TSO ----------------
    customers = frappe.db.sql("""
        SELECT
            c.name AS customer,
            st.sales_person AS tso
        FROM `tabCustomer` c
        JOIN `tabSales Team` st
            ON st.parent = c.name
           AND st.parenttype = 'Customer'
    """, as_dict=True)

    # ---------------- TARGETS ----------------
    targets = frappe.db.sql("""
        SELECT
            sales_person,
            SUM(
                CASE %(month)s
                    WHEN 1 THEN custom_january
                    WHEN 2 THEN custom_february
                    WHEN 3 THEN custom_march
                    WHEN 4 THEN custom_april
                    WHEN 5 THEN custom_may_
                    WHEN 6 THEN custom_june
                    WHEN 7 THEN custom_july
                    WHEN 8 THEN custom_august
                    WHEN 9 THEN custom_september
                    WHEN 10 THEN custom_october
                    WHEN 11 THEN custom_november
                    WHEN 12 THEN custom_december
                END
            ) AS month_target,
            SUM(
                custom_january + custom_february + custom_march +
                custom_april + custom_may_ + custom_june +
                custom_july + custom_august + custom_september +
                custom_october + custom_november + custom_december
            ) AS ytd_target
        FROM `tabSales Team`
        WHERE parenttype = 'Customer'
        GROUP BY sales_person
    """, {"month": month}, as_dict=True)

    target_map = {t.sales_person: t for t in targets}

    # ---------------- ACHIEVED ----------------
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

    ach_map, ach_drill = {}, {}
    for r in achieved_rows:
        ach_map.setdefault(r.sales_person, 0)
        ach_map[r.sales_person] += flt(r.base_net_total)
        ach_drill.setdefault(r.sales_person, []).append({
            "invoice": r.invoice,
            "date": str(r.posting_date),
            "amount": flt(r.base_net_total)
        })

    ytd_ach = frappe.db.sql("""
        SELECT
            st.sales_person,
            SUM(si.base_net_total) AS achieved
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
          AND YEAR(si.posting_date) = %s
        GROUP BY st.sales_person
    """, year, as_dict=True)

    ytd_ach_map = {r.sales_person: flt(r.achieved) for r in ytd_ach}

    # ---------------- OUTSTANDING ----------------
    invoices = frappe.db.sql("""
        SELECT customer, outstanding_amount, due_date
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND outstanding_amount > 0
    """, as_dict=True)

    out_map, overdue_map = {}, {}
    for i in invoices:
        out_map.setdefault(i.customer, 0)
        overdue_map.setdefault(i.customer, 0)

        out_map[i.customer] += flt(i.outstanding_amount)
        if i.due_date and getdate(i.due_date) < getdate(today()):
            overdue_map[i.customer] += flt(i.outstanding_amount)

    # ---------------- FINAL RESULT ----------------
    result = []

    for c in customers:
        tso = c.tso
        if tso not in sp_map:
            continue

        asm = sp_map[tso].parent_sales_person
        rsm = sp_map.get(asm, {}).get("parent_sales_person") if asm else None

        t = target_map.get(tso, {})
        mt = flt(getattr(t, "month_target", 0))
        yt = flt(getattr(t, "ytd_target", 0))

        ma = flt(ach_map.get(tso))
        ya = flt(ytd_ach_map.get(tso))

        result.append({
            "customer": c.customer,
            "rsm": rsm,
            "asm": asm,
            "tso": tso,
            "region": sp_map[tso].custom_region,
            "territory": sp_map[tso].custom_territory,
            "location": sp_map[tso].custom_location,

            "month_target": mt,
            "month_achieved": ma,
            "month_pct": (ma / mt * 100) if mt else 0,

            "ytd_target": yt,
            "ytd_achieved": ya,
            "ytd_pct": (ya / yt * 100) if yt else 0,

            "outstanding": out_map.get(c.customer, 0),
            "overdue": overdue_map.get(c.customer, 0),

            "achieved_drill": frappe.as_json(ach_drill.get(tso, []))
        })

    return result
