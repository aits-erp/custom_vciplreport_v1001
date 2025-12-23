import frappe
from frappe.utils import today, getdate, date_diff


def execute(filters=None):
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "Customer Group", "fieldname": "customer_group",
         "fieldtype": "Link", "options": "Customer Group", "width": 140},

        {"label": "Distributor", "fieldname": "customer",
         "fieldtype": "Data", "width": 260},

        {"label": "RSM", "fieldname": "rsm",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "ASM", "fieldname": "asm",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "TSO", "fieldname": "tso",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "Total Outstanding", "fieldname": "total_outstanding",
         "fieldtype": "Currency", "width": 160},

        {"label": "Total Overdue", "fieldname": "total_overdue",
         "fieldtype": "Currency", "width": 160},

        {"label": "Average Overdue Days", "fieldname": "avg_overdue_days",
         "fieldtype": "Float", "precision": 2, "width": 170},

        {"label": "Average Payment Days", "fieldname": "avg_payment_days",
         "fieldtype": "Float", "precision": 2, "width": 170},

        # hidden drill helpers
        {"label": "Customer Code", "fieldname": "customer_code", "hidden": 1},
        {"label": "Outstanding Drill", "fieldname": "outstanding_drill", "hidden": 1},
        {"label": "Overdue Drill", "fieldname": "overdue_drill", "hidden": 1},
        {"label": "Avg Overdue Drill", "fieldname": "avg_overdue_drill", "hidden": 1},
        {"label": "Avg Payment Drill", "fieldname": "avg_payment_drill", "hidden": 1},
    ]


# --------------------------------------------------
# MAIN DATA
# --------------------------------------------------
def get_data(filters=None):

    tso_filter = filters.get("tso") if filters else None
    asm_filter = filters.get("asm") if filters else None
    rsm_filter = filters.get("rsm") if filters else None

    # ---------------- SALES INVOICES ----------------
    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer,
            si.customer_name,
            si.customer_group,
            si.posting_date,
            si.outstanding_amount
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.customer_group = 'Distributor'
    """, as_dict=True)

    if not invoices:
        return []

    # ---------------- PAYMENT SCHEDULE ----------------
    payment_terms = frappe.db.sql("""
        SELECT parent, due_date
        FROM `tabPayment Schedule`
    """, as_dict=True)

    due_map = {}
    for p in payment_terms:
        due_map.setdefault(p.parent, []).append(p.due_date)

    # ---------------- PAYMENT ENTRY ----------------
    payments = frappe.db.sql("""
        SELECT
            per.reference_name AS invoice,
            pe.posting_date AS payment_date
        FROM `tabPayment Entry Reference` per
        JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE per.reference_doctype = 'Sales Invoice'
          AND pe.docstatus = 1
    """, as_dict=True)

    pay_map = {}
    for p in payments:
        pay_map.setdefault(p.invoice, []).append(p.payment_date)

    # ---------------- CUSTOMER SALES TEAM ----------------
    sales_team = frappe.db.sql("""
        SELECT
            st.parent AS customer,
            st.sales_person
        FROM `tabSales Team` st
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    cust_sales_map = {}
    for s in sales_team:
        cust_sales_map.setdefault(s.customer, []).append(s.sales_person)

    cust_map = {}

    # ---------------- PROCESS INVOICES ----------------
    for inv in invoices:
        cust = inv.customer

        if cust not in cust_map:
            cust_map[cust] = {
                "customer_code": cust,
                "customer_name": inv.customer_name,
                "customer_group": inv.customer_group,
                "total_outstanding": 0,
                "total_overdue": 0,
                "outstanding_list": [],
                "overdue_list": [],
                "avg_overdue_list": [],
                "avg_payment_list": [],
            }

        cust_map[cust]["total_outstanding"] += inv.outstanding_amount

        due_dates = due_map.get(inv.invoice, [])
        due_date = due_dates[0] if due_dates else None

        overdue_days = (
            date_diff(today(), due_date)
            if due_date and getdate(today()) > getdate(due_date)
            else None
        )

        cust_map[cust]["outstanding_list"].append({
            "invoice": inv.invoice,
            "posting_date": str(inv.posting_date),
            "due_date": str(due_date) if due_date else "-",
            "amount": float(inv.outstanding_amount),
            "days": overdue_days if overdue_days else "-"
        })

        if overdue_days:
            cust_map[cust]["total_overdue"] += inv.outstanding_amount
            cust_map[cust]["overdue_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "due_date": str(due_date),
                "amount": float(inv.outstanding_amount),
                "overdue_days": overdue_days,
            })
            cust_map[cust]["avg_overdue_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "due_date": str(due_date),
                "amount": float(inv.outstanding_amount),
                "days": overdue_days,
            })

        for pay_date in pay_map.get(inv.invoice, []):
            days = date_diff(pay_date, inv.posting_date)
            cust_map[cust]["avg_payment_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "payment_date": str(pay_date),
                "amount": float(inv.outstanding_amount),
                "days": days,
            })

    # ---------------- FINAL RESULT ----------------
    result = []

    for cust, row in cust_map.items():

        tso = None
        asm = None
        rsm = None

        for sp in cust_sales_map.get(cust, []):
            tso = sp
            asm = frappe.db.get_value("Sales Person", tso, "parent_sales_person")
            if asm:
                rsm = frappe.db.get_value("Sales Person", asm, "parent_sales_person")

        # -------- APPLY FILTERS --------
        if tso_filter and tso != tso_filter:
            continue
        if asm_filter and asm != asm_filter:
            continue
        if rsm_filter and rsm != rsm_filter:
            continue

        avg_overdue = (
            sum(i["days"] for i in row["avg_overdue_list"]) / len(row["avg_overdue_list"])
            if row["avg_overdue_list"] else 0
        )

        avg_payment = (
            sum(i["days"] for i in row["avg_payment_list"]) / len(row["avg_payment_list"])
            if row["avg_payment_list"] else 0
        )

        result.append({
            "customer_group": row["customer_group"],
            "customer": row["customer_name"],
            "customer_code": row["customer_code"],
            "tso": tso,
            "asm": asm,
            "rsm": rsm,
            "total_outstanding": row["total_outstanding"],
            "total_overdue": row["total_overdue"],
            "avg_overdue_days": avg_overdue,
            "avg_payment_days": avg_payment,
            "outstanding_drill": frappe.as_json(row["outstanding_list"]),
            "overdue_drill": frappe.as_json(row["overdue_list"]),
            "avg_overdue_drill": frappe.as_json(row["avg_overdue_list"]),
            "avg_payment_drill": frappe.as_json(row["avg_payment_list"]),
        })

    return result
