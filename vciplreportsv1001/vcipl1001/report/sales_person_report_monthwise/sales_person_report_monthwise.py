import frappe
from frappe.utils import getdate, nowdate, flt


def execute(filters=None):
    return get_columns(), get_data(filters or {})


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():

    months = [
        ("jan", "January"), ("feb", "February"), ("mar", "March"),
        ("apr", "April"), ("may", "May"), ("jun", "June"),
        ("jul", "July"), ("aug", "August"), ("sep", "September"),
        ("oct", "October"), ("nov", "November"), ("dec", "December"),
    ]

    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link",
         "options": "Customer", "width": 140},

        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link",
         "options": "Sales Person", "width": 160},

        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 90},
    ]

    for m, lbl in months:
        columns += [
            {"label": f"{lbl} Target", "fieldname": f"{m}_target",
             "fieldtype": "Currency", "width": 130},

            {"label": f"{lbl} Ach", "fieldname": f"{m}_ach",
             "fieldtype": "Currency", "width": 130},

            {"label": f"{lbl} %", "fieldname": f"{m}_pct",
             "fieldtype": "Float", "precision": 2, "width": 90},
        ]

    columns += [
        {"label": "Total Target", "fieldname": "total_target",
         "fieldtype": "Currency", "width": 150},

        {"label": "Total Ach", "fieldname": "total_ach",
         "fieldtype": "Currency", "width": 150},

        {"label": "Total %", "fieldname": "total_pct",
         "fieldtype": "Float", "precision": 2, "width": 100},

        # drill helpers
        {"label": "Ach Drill", "fieldname": "ach_drill", "hidden": 1},
    ]

    return columns


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    year = int(filters.get("year") or getdate(nowdate()).year)

    # -----------------------------
    # TARGETS (Customer → Sales Team)
    # -----------------------------
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
            st.custom_december  AS dec
        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    # -----------------------------
    # ACHIEVEMENTS (Sales Invoice)
    # -----------------------------
    invoices = frappe.db.sql("""
        SELECT
            si.name,
            si.customer,
            si.posting_date,
            si.base_net_total,
            st.sales_person,
            st.allocated_percentage
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st
            ON st.parent = si.name
           AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
          AND YEAR(si.posting_date) = %s
    """, year, as_dict=True)

    data = {}

    # -----------------------------
    # BUILD TARGET MAP
    # -----------------------------
    for t in targets:

        key = (t.customer, t.sales_person)

        data.setdefault(key, {
            "customer": t.customer,
            "sales_person": t.sales_person,
            "role": get_role(t.sales_person),
            "targets": {},
            "ach": {},
            "drill": []
        })

        for m in ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]:
            data[key]["targets"][m] = flt(t.get(m))

    # -----------------------------
    # APPLY ACHIEVEMENT
    # -----------------------------
    for inv in invoices:

        key = (inv.customer, inv.sales_person)
        if key not in data:
            continue

        month = getdate(inv.posting_date).strftime("%b").lower()[:3]

        amt = flt(inv.base_net_total) * flt(inv.allocated_percentage) / 100

        data[key]["ach"].setdefault(month, 0)
        data[key]["ach"][month] += amt

        data[key]["drill"].append({
            "invoice": inv.name,
            "date": str(inv.posting_date),
            "amount": amt
        })

    # -----------------------------
    # FINAL ROWS
    # -----------------------------
    rows = []

    for row in data.values():

        out = {
            "customer": row["customer"],
            "sales_person": row["sales_person"],
            "role": row["role"],
            "total_target": 0,
            "total_ach": 0,
            "ach_drill": frappe.as_json(row["drill"])
        }

        for m in ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]:

            tgt = flt(row["targets"].get(m))
            ach = flt(row["ach"].get(m))

            out[f"{m}_target"] = tgt
            out[f"{m}_ach"] = ach
            out[f"{m}_pct"] = (ach / tgt * 100) if tgt else 0

            out["total_target"] += tgt
            out["total_ach"] += ach

        out["total_pct"] = (out["total_ach"] / out["total_target"] * 100) if out["total_target"] else 0

        rows.append(out)

    return rows


# --------------------------------------------------
# ROLE DETECTION
# --------------------------------------------------
def get_role(sp):
    parent = frappe.db.get_value("Sales Person", sp, "parent_sales_person")
    if not parent:
        return "TSO"

    if parent.upper().startswith("ASM"):
        return "TSO"
    if parent.upper().startswith("RSM"):
        return "ASM"

    return "TSO"
