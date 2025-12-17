import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    columns = [
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 220
        }
    ]

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in months:
        columns.append({
            "label": f"{m} Target",
            "fieldname": f"{m.lower()}_target",
            "fieldtype": "Currency",
            "width": 120
        })
        columns.append({
            "label": f"{m} Ach",
            "fieldname": f"{m.lower()}_ach",
            "fieldtype": "Currency",
            "width": 120
        })
        columns.append({
            "label": f"{m} %",
            "fieldname": f"{m.lower()}_pct",
            "fieldtype": "Percent",
            "width": 90
        })

    columns.extend([
        {
            "label": "Total Target",
            "fieldname": "total_target",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total Ach",
            "fieldname": "total_ach",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total %",
            "fieldname": "total_pct",
            "fieldtype": "Percent",
            "width": 120
        }
    ])

    return columns


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    sales_person = filters.get("sales_person")

    # 🔑 IMPORTANT: do NOT throw error
    if not sales_person:
        return []

    # 1️⃣ Customer Targets
    targets = frappe.db.sql("""
        SELECT
            c.name AS customer,
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
        WHERE st.sales_person = %s
          AND c.disabled = 0
    """, sales_person, as_dict=True)

    # 2️⃣ Achievements (Sales Invoice)
    invoices = frappe.db.sql("""
        SELECT
            si.customer,
            MONTH(si.posting_date) AS month,
            SUM(si.base_net_total) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st
            ON st.parent = si.name
        WHERE si.docstatus = 1
          AND st.sales_person = %s
        GROUP BY si.customer, MONTH(si.posting_date)
    """, sales_person, as_dict=True)

    ach_map = {}
    for r in invoices:
        ach_map.setdefault(r.customer, {})[r.month] = flt(r.amount)

    result = []

    for t in targets:
        row = {"customer": t.customer}

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
            ach = flt(ach_map.get(t.customer, {}).get(m_no))
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
