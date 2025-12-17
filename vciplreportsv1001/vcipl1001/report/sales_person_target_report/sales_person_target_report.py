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
    year = filters.get("year")

    if not sales_person:
        return []

    # -----------------------------
    # CUSTOMER LIST (BASE)
    # -----------------------------
    customers = frappe.db.sql("""
        SELECT DISTINCT
            st.parent AS customer
        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
          AND st.sales_person = %s
    """, sales_person, as_dict=True)

    if not customers:
        return []

    customer_names = [c.customer for c in customers]

    # -----------------------------
    # TARGETS
    # -----------------------------
    targets = frappe.db.sql("""
        SELECT
            parent AS customer,
            custom_january   AS jan,
            custom_february  AS feb,
            custom_march     AS mar,
            custom_april     AS apr,
            custom_may_      AS may,
            custom_june      AS jun,
            custom_july      AS jul,
            custom_august    AS aug,
            custom_september AS sep,
            custom_october   AS oct,
            custom_november  AS nov,
            custom_december  AS dec_val
        FROM `tabSales Team`
        WHERE parenttype = 'Customer'
          AND sales_person = %s
    """, sales_person, as_dict=True)

    target_map = {t.customer: t for t in targets}

    # -----------------------------
    # ACHIEVEMENTS
    # -----------------------------
    conditions = ""
    values = [sales_person]

    if year:
        conditions += " AND YEAR(si.posting_date) = %s"
        values.append(year)

    invoices = frappe.db.sql(f"""
        SELECT
            si.customer,
            MONTH(si.posting_date) AS month,
            SUM(si.base_net_total) AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
          AND st.sales_person = %s
          {conditions}
        GROUP BY si.customer, MONTH(si.posting_date)
    """, values, as_dict=True)

    ach_map = {}
    for r in invoices:
        ach_map.setdefault(r.customer, {})[r.month] = flt(r.amount)

    # -----------------------------
    # FINAL RESULT
    # -----------------------------
    result = []

    for cust in customer_names:
        t = target_map.get(cust, {})

        row = {"customer": cust}
        total_target = 0
        total_ach = 0

        month_targets = {
            1: flt(getattr(t, "jan", 0)),
            2: flt(getattr(t, "feb", 0)),
            3: flt(getattr(t, "mar", 0)),
            4: flt(getattr(t, "apr", 0)),
            5: flt(getattr(t, "may", 0)),
            6: flt(getattr(t, "jun", 0)),
            7: flt(getattr(t, "jul", 0)),
            8: flt(getattr(t, "aug", 0)),
            9: flt(getattr(t, "sep", 0)),
            10: flt(getattr(t, "oct", 0)),
            11: flt(getattr(t, "nov", 0)),
            12: flt(getattr(t, "dec_val", 0)),
        }

        for m_no, m_key in zip(
            range(1, 13),
            ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
        ):
            target = month_targets[m_no]
            ach = flt(ach_map.get(cust, {}).get(m_no))
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
