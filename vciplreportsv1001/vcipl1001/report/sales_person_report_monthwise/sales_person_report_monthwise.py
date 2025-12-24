import frappe
from frappe.utils import getdate, flt


# ==========================================================
# EXECUTE
# ==========================================================
def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# ==========================================================
# COLUMNS
# ==========================================================
def get_columns():
    cols = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 140},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 90},
    ]

    months = [
        ("jan", "January"), ("feb", "February"), ("mar", "March"),
        ("apr", "April"), ("may", "May"), ("jun", "June"),
        ("jul", "July"), ("aug", "August"), ("sep", "September"),
        ("oct", "October"), ("nov", "November"), ("dec_m", "December")
    ]

    for m, label in months:
        cols.extend([
            {"label": f"{label} Target", "fieldname": f"{m}_target", "fieldtype": "Currency", "width": 130},
            {"label": f"{label} Achieved", "fieldname": f"{m}_ach", "fieldtype": "Currency", "width": 130},
            {"label": f"{label} %", "fieldname": f"{m}_pct", "fieldtype": "Percent", "width": 90},
        ])

    cols.extend([
        {"label": "Total Target", "fieldname": "total_target", "fieldtype": "Currency", "width": 140},
        {"label": "Total Achieved", "fieldname": "total_ach", "fieldtype": "Currency", "width": 140},
        {"label": "Total %", "fieldname": "total_pct", "fieldtype": "Percent", "width": 100},
    ])

    return cols


# ==========================================================
# DATA
# ==========================================================
def get_data(filters):

    year = int(filters.get("year") or getdate().year)

    # ------------------------------------------------------
    # TARGETS (Customer → Sales Team)
    # ------------------------------------------------------
    targets = frappe.db.sql("""
        SELECT
            st.parent AS customer,
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
            st.custom_december  AS dec_m

        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    data = {}

    for t in targets:
        key = (t.customer, t.sales_person)
        data[key] = {
            "customer": t.customer,
            "sales_person": t.sales_person,
            "role": get_role(t.sales_person),
            "targets": {
                "jan": flt(t.jan), "feb": flt(t.feb), "mar": flt(t.mar),
                "apr": flt(t.apr), "may": flt(t.may), "jun": flt(t.jun),
                "jul": flt(t.jul), "aug": flt(t.aug), "sep": flt(t.sep),
                "oct": flt(t.oct), "nov": flt(t.nov), "dec_m": flt(t.dec_m),
            },
            "ach": {m: 0 for m in ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec_m"]}
        }

    # ------------------------------------------------------
    # ACHIEVEMENTS (Sales Invoice)
    # ------------------------------------------------------
    invoices = frappe.db.sql("""
        SELECT
            si.customer,
            st.sales_person,
            si.posting_date,
            si.base_net_total
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
          AND YEAR(si.posting_date) = %s
    """, year, as_dict=True)

    for inv in invoices:
        key = (inv.customer, inv.sales_person)
        if key not in data:
            continue

        month = getdate(inv.posting_date).month
        month_map = {
            1:"jan",2:"feb",3:"mar",4:"apr",5:"may",6:"jun",
            7:"jul",8:"aug",9:"sep",10:"oct",11:"nov",12:"dec_m"
        }

        data[key]["ach"][month_map[month]] += flt(inv.base_net_total)

    # ------------------------------------------------------
    # FINAL ROW BUILD
    # ------------------------------------------------------
    result = []

    for row in data.values():
        out = {
            "customer": row["customer"],
            "sales_person": row["sales_person"],
            "role": row["role"],
        }

        total_target = 0
        total_ach = 0

        for m in row["targets"]:
            tgt = row["targets"][m]
            ach = row["ach"][m]

            out[f"{m}_target"] = tgt
            out[f"{m}_ach"] = ach
            out[f"{m}_pct"] = (ach / tgt * 100) if tgt else 0

            total_target += tgt
            total_ach += ach

        out["total_target"] = total_target
        out["total_ach"] = total_ach
        out["total_pct"] = (total_ach / total_target * 100) if total_target else 0

        result.append(out)

    return result


# ==========================================================
# ROLE
# ==========================================================
def get_role(sales_person):
    parent = frappe.db.get_value("Sales Person", sales_person, "parent_sales_person")
    if not parent:
        return "TSO"
    return parent.split("-")[0].upper()
