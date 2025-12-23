import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "#", "fieldname": "sr_no", "fieldtype": "Int", "width": 50},

        {"label": "Main Group", "fieldname": "main_group", "fieldtype": "Data", "width": 140},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 200},

        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 80},
        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 120},

        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved", "fieldname": "achieved", "fieldtype": "Currency", "width": 140},
        {"label": "%", "fieldname": "pct", "fieldtype": "Percent", "width": 80},

        {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 150},
        {"label": "Total Achieved", "fieldname": "total_achieved", "fieldtype": "Currency", "width": 150},
        {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 100},
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    main_group_filter = filters.get("main_group")
    customer_filter = filters.get("customer")
    sales_person_filter = filters.get("sales_person")

    conditions = ""
    values = [month, year]

    if main_group_filter:
        conditions += " AND it.custom_main_group = %s"
        values.append(main_group_filter)

    if customer_filter:
        conditions += " AND si.customer = %s"
        values.append(customer_filter)

    if sales_person_filter:
        conditions += " AND st.sales_person = %s"
        values.append(sales_person_filter)

    # ---------------- TARGETS ----------------
    targets = frappe.db.sql("""
        SELECT
            st.sales_person,
            SUM(
                CASE %s
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
    """, (month,), as_dict=True)

    target_map = {t.sales_person: t for t in targets}

    # ---------------- ACHIEVED (MONTH) ----------------
    achieved = frappe.db.sql(f"""
        SELECT
            st.sales_person,
            si.customer,
            it.custom_main_group AS main_group,
            SUM(sii.base_net_amount) AS achieved
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` it ON it.name = sii.item_code
        WHERE si.docstatus = 1
          AND MONTH(si.posting_date) = %s
          AND YEAR(si.posting_date) = %s
          {conditions}
        GROUP BY st.sales_person, si.customer, it.custom_main_group
    """, tuple(values), as_dict=True)

    # ---------------- TOTAL ACHIEVED ----------------
    total_achieved = frappe.db.sql(f"""
        SELECT
            st.sales_person,
            si.customer,
            it.custom_main_group AS main_group,
            SUM(sii.base_net_amount) AS achieved
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` it ON it.name = sii.item_code
        WHERE si.docstatus = 1
          AND YEAR(si.posting_date) = %s
          {conditions}
        GROUP BY st.sales_person, si.customer, it.custom_main_group
    """, (year, *values[2:]), as_dict=True)

    total_ach_map = {
        (a.sales_person, a.customer, a.main_group): flt(a.achieved)
        for a in total_achieved
    }

    # ---------------- FINAL RESULT ----------------
    result = []
    sr_no = 1

    for a in achieved:
        t = target_map.get(a.sales_person)
        if not t:
            continue

        role, region = get_role_and_region(a.sales_person)

        month_target = flt(t.month_target)
        month_ach = flt(a.achieved)
        month_pct = (month_ach / month_target * 100) if month_target else 0

        tot_target = flt(t.total_target)
        tot_ach = flt(total_ach_map.get((a.sales_person, a.customer, a.main_group)))
        tot_pct = (tot_ach / tot_target * 100) if tot_target else 0

        result.append({
            "sr_no": sr_no,
            "main_group": a.main_group,
            "customer": a.customer,
            "sales_person": a.sales_person,
            "role": role,
            "region": region,
            "target": month_target,
            "achieved": month_ach,
            "pct": month_pct,
            "total_target": tot_target,
            "total_achieved": tot_ach,
            "total_pct": tot_pct,
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
