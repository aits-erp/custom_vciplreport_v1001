import frappe
from frappe.utils import today, getdate, date_diff, flt


def execute(filters=None):
    return get_columns(), get_data(filters)


# --------------------------------------------------
# FISCAL YEAR -> DATE RANGE
# --------------------------------------------------
def get_dates(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    fiscal_year = filters.get("fiscal_year")

    # if dates weren't set manually, derive them from the fiscal year
    if (not from_date or not to_date) and fiscal_year:
        fy = frappe.db.get_value(
            "Fiscal Year",
            fiscal_year,
            ["year_start_date", "year_end_date"],
            as_dict=True
        )
        if fy:
            from_date = from_date or fy.year_start_date
            to_date = to_date or fy.year_end_date

    return from_date, to_date


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 140},
        {"label": "Distributor", "fieldname": "customer", "fieldtype": "Data", "width": 260},
        {"label": "Region", "fieldname": "region", "fieldtype": "Data", "width": 140},
        {"label": "RSM", "fieldname": "rsm", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": "ASM", "fieldname": "asm", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": "TSO", "fieldname": "tso", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": "Total Outstanding", "fieldname": "total_outstanding", "fieldtype": "Currency", "width": 160},
        {"label": "Total Overdue", "fieldname": "total_overdue", "fieldtype": "Currency", "width": 160},
        {"label": "0-15 Days", "fieldname": "aging_0_15", "fieldtype": "Currency", "width": 120},
        {"label": "16-30 Days", "fieldname": "aging_16_30", "fieldtype": "Currency", "width": 120},
        {"label": "31+ Days", "fieldname": "aging_31_45", "fieldtype": "Currency", "width": 120},
        {"label": "Average Overdue Days", "fieldname": "avg_overdue_days", "fieldtype": "Float", "precision": 2, "width": 170},
        {"label": "Average Payment Days", "fieldname": "avg_payment_days", "fieldtype": "Float", "precision": 2, "width": 170},

        # hidden fields
        {"label": "Customer Code", "fieldname": "customer_code", "hidden": 1},
        {"label": "Outstanding Drill", "fieldname": "outstanding_drill", "hidden": 1},
        {"label": "Overdue Drill", "fieldname": "overdue_drill", "hidden": 1},
        {"label": "Avg Overdue Drill", "fieldname": "avg_overdue_drill", "hidden": 1},
        {"label": "Avg Payment Drill", "fieldname": "avg_payment_drill", "hidden": 1},
        {"label": "Aging 0-15 Drill", "fieldname": "aging_0_15_drill", "hidden": 1},
        {"label": "Aging 16-30 Drill", "fieldname": "aging_16_30_drill", "hidden": 1},
        {"label": "Aging 31-45 Drill", "fieldname": "aging_31_45_drill", "hidden": 1},
    ]


# --------------------------------------------------
# MAIN DATA
# --------------------------------------------------
def get_data(filters=None):

    filters = filters or {}

    customer_group = filters.get("customer_group")
    from_date, to_date = get_dates(filters)

    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer,
            si.customer_name,
            si.customer_group,
            si.posting_date,
            si.outstanding_amount,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        AND (%(customer_group)s IS NULL OR si.customer_group = %(customer_group)s)
        AND (%(from_date)s IS NULL OR si.posting_date >= %(from_date)s)
        AND (%(to_date)s   IS NULL OR si.posting_date <= %(to_date)s)
    """, {
        "customer_group": customer_group,
        "from_date": from_date,
        "to_date": to_date,
    }, as_dict=True)

    if not invoices:
        return []

    # PAYMENT SCHEDULE
    payment_terms = frappe.db.sql("""
        SELECT parent, due_date FROM `tabPayment Schedule`
    """, as_dict=True)

    due_map = {}
    for p in payment_terms:
        due_map.setdefault(p.parent, []).append(p.due_date)

    # PAYMENT ENTRIES
    payments = frappe.db.sql("""
        SELECT per.reference_name AS invoice, pe.posting_date AS payment_date
        FROM `tabPayment Entry Reference` per
        INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE per.reference_doctype = 'Sales Invoice' AND pe.docstatus = 1
    """, as_dict=True)

    pay_map = {}
    for p in payments:
        pay_map.setdefault(p.invoice, []).append(p.payment_date)

    # SALES TEAM
    sales_team = frappe.db.sql("""
        SELECT st.parent AS customer, st.sales_person, sp.custom_region
        FROM `tabSales Team` st
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    cust_sales_map = {}
    cust_region_map = {}
    for s in sales_team:
        cust_sales_map.setdefault(s.customer, []).append(s.sales_person)
        if s.customer not in cust_region_map:
            cust_region_map[s.customer] = s.custom_region

    cust_map = {}

    # PROCESS INVOICES
    for inv in invoices:

        cust = inv.customer

        if cust not in cust_map:
            cust_map[cust] = {
                "customer_code": cust,
                "customer_name": inv.customer_name,
                "customer_group": inv.customer_group,
                "region": cust_region_map.get(cust, ""),
                "total_outstanding": 0,
                "total_overdue": 0,
                "aging_0_15": 0,
                "aging_16_30": 0,
                "aging_31_45": 0,
                "outstanding_list": [],
                "overdue_list": [],
                "avg_overdue_list": [],
                "avg_payment_list": [],
                "aging_0_15_list": [],
                "aging_16_30_list": [],
                "aging_31_45_list": [],
            }

        cust_map[cust]["total_outstanding"] += flt(inv.outstanding_amount)

        due_dates = due_map.get(inv.invoice, [])
        due_date = due_dates[0] if due_dates else None

        overdue_days = None
        if due_date and getdate(today()) > getdate(due_date):
            overdue_days = date_diff(today(), due_date)

        # ONLY OPEN INVOICES IN POPUPS
        if flt(inv.outstanding_amount) > 0:

            cust_map[cust]["outstanding_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "due_date": str(due_date) if due_date else "-",
                "amount": flt(inv.outstanding_amount),
                "days": overdue_days if overdue_days else "-"
            })

            if overdue_days:

                cust_map[cust]["total_overdue"] += flt(inv.outstanding_amount)

                if 0 <= overdue_days <= 15:
                    cust_map[cust]["aging_0_15"] += flt(inv.outstanding_amount)
                    cust_map[cust]["aging_0_15_list"].append({
                        "invoice": inv.invoice, "posting_date": str(inv.posting_date),
                        "due_date": str(due_date), "amount": flt(inv.outstanding_amount),
                        "days": overdue_days
                    })
                elif 16 <= overdue_days <= 30:
                    cust_map[cust]["aging_16_30"] += flt(inv.outstanding_amount)
                    cust_map[cust]["aging_16_30_list"].append({
                        "invoice": inv.invoice, "posting_date": str(inv.posting_date),
                        "due_date": str(due_date), "amount": flt(inv.outstanding_amount),
                        "days": overdue_days
                    })
                else:
                    cust_map[cust]["aging_31_45"] += flt(inv.outstanding_amount)
                    cust_map[cust]["aging_31_45_list"].append({
                        "invoice": inv.invoice, "posting_date": str(inv.posting_date),
                        "due_date": str(due_date), "amount": flt(inv.outstanding_amount),
                        "days": overdue_days
                    })

                cust_map[cust]["overdue_list"].append({
                    "invoice": inv.invoice, "posting_date": str(inv.posting_date),
                    "due_date": str(due_date), "amount": flt(inv.outstanding_amount),
                    "overdue_days": overdue_days
                })

                cust_map[cust]["avg_overdue_list"].append({
                    "invoice": inv.invoice, "posting_date": str(inv.posting_date),
                    "due_date": str(due_date), "amount": flt(inv.outstanding_amount),
                    "days": overdue_days
                })

        # PAYMENT DAYS POPUP
        for pay_date in pay_map.get(inv.invoice, []):
            days = date_diff(pay_date, inv.posting_date)
            cust_map[cust]["avg_payment_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "payment_date": str(pay_date),
                "amount": flt(inv.grand_total),
                "days": days
            })

    # FINAL RESULT
    result = []
    for cust, row in cust_map.items():

        tso = asm = rsm = None

        for sp in cust_sales_map.get(cust, []):
            parent = frappe.db.get_value("Sales Person", sp, "parent_sales_person")
            if not parent:
                continue
            parent_name = parent.lower()
            if parent_name.startswith("tso") and not tso:
                tso = sp
            elif parent_name.startswith("asm") and not asm:
                asm = sp
            elif parent_name.startswith("rsm") and not rsm:
                rsm = sp

        avg_overdue = 0
        if row["avg_overdue_list"]:
            avg_overdue = sum(i["days"] for i in row["avg_overdue_list"]) / len(row["avg_overdue_list"])

        avg_payment = 0
        if row["avg_payment_list"]:
            avg_payment = sum(i["days"] for i in row["avg_payment_list"]) / len(row["avg_payment_list"])

        result.append({
            "customer_group": row["customer_group"],
            "customer": row["customer_name"],
            "region": row["region"],
            "customer_code": row["customer_code"],
            "rsm": rsm,
            "asm": asm,
            "tso": tso,
            "total_outstanding": row["total_outstanding"],
            "total_overdue": row["total_overdue"],
            "avg_overdue_days": avg_overdue,
            "avg_payment_days": avg_payment,
            "aging_0_15": row["aging_0_15"],
            "aging_16_30": row["aging_16_30"],
            "aging_31_45": row["aging_31_45"],
            "outstanding_drill": frappe.as_json(row["outstanding_list"]),
            "overdue_drill": frappe.as_json(row["overdue_list"]),
            "avg_overdue_drill": frappe.as_json(row["avg_overdue_list"]),
            "avg_payment_drill": frappe.as_json(row["avg_payment_list"]),
            "aging_0_15_drill": frappe.as_json(row["aging_0_15_list"]),
            "aging_16_30_drill": frappe.as_json(row["aging_16_30_list"]),
            "aging_31_45_drill": frappe.as_json(row["aging_31_45_list"]),
        })

    return result