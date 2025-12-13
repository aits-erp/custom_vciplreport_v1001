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

        {"label": "ASM", "fieldname": "asm",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "RSM", "fieldname": "rsm",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "Total Outstanding", "fieldname": "total_outstanding",
         "fieldtype": "Currency", "width": 160},

        {"label": "Total Overdue", "fieldname": "total_overdue",
         "fieldtype": "Currency", "width": 160},

        {"label": "Average Overdue Days", "fieldname": "avg_overdue_days",
         "fieldtype": "Float", "precision": 2, "width": 170},

        {"label": "Average Payment Days", "fieldname": "avg_payment_days",
         "fieldtype": "Float", "precision": 2, "width": 170},

        # hidden drilldown payloads
        {"label": "Outstanding Drill", "fieldname": "outstanding_drill", "hidden": 1},
        {"label": "Overdue Drill", "fieldname": "overdue_drill", "hidden": 1},
        {"label": "Avg Overdue Drill", "fieldname": "avg_overdue_drill", "hidden": 1},
        {"label": "Avg Payment Drill", "fieldname": "avg_payment_drill", "hidden": 1},
    ]


# --------------------------------------------------
# MAIN DATA
# --------------------------------------------------
def get_data(filters=None):

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

    # ---------------- CUSTOMER SALES TEAM (SOURCE OF TRUTH) ----------------
    sales_team = frappe.db.sql("""
        SELECT
            st.parent AS customer,
            st.sales_person,
            sp.sales_person_name
        FROM `tabSales Team` st
        JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    sales_map = {}
    for s in sales_team:
        sales_map.setdefault(s.customer, []).append(s)

    cust_map = {}

    # ---------------- PROCESS INVOICES ----------------
    for inv in invoices:
        cust = inv.customer

        if cust not in cust_map:
            cust_map[cust] = {
                "customer": inv.customer_name,
                "customer_group": inv.customer_group,
                "total_outstanding": 0,
                "total_overdue": 0,
                "outstanding_list": [],
                "overdue_list": [],
                "avg_overdue_list": [],
                "avg_payment_list": [],
            }

        cust_map[cust]["total_outstanding"] += inv.outstanding_amount

        # outstanding drill
        cust_map[cust]["outstanding_list"].append({
            "invoice": inv.invoice,
            "posting_date": str(inv.posting_date),
            "amount": float(inv.outstanding_amount),
        })

        # overdue logic
        for due in due_map.get(inv.invoice, []):
            if due and getdate(today()) > getdate(due):
                overdue_days = date_diff(today(), due)
                cust_map[cust]["total_overdue"] += inv.outstanding_amount

                cust_map[cust]["overdue_list"].append({
                    "invoice": inv.invoice,
                    "posting_date": str(inv.posting_date),
                    "due_date": str(due),
                    "amount": float(inv.outstanding_amount),
                    "overdue_days": overdue_days,
                })

                cust_map[cust]["avg_overdue_list"].append({
                    "invoice": inv.invoice,
                    "posting_date": str(inv.posting_date),
                    "due_date": str(due),
                    "days": overdue_days,
                })

        # payment days logic
        for pay_date in pay_map.get(inv.invoice, []):
            days = date_diff(pay_date, inv.posting_date)
            cust_map[cust]["avg_payment_list"].append({
                "invoice": inv.invoice,
                "posting_date": str(inv.posting_date),
                "payment_date": str(pay_date),
                "days": days,
            })

    # ---------------- FINAL RESULT ----------------
    result = []

    for cust, row in cust_map.items():

        avg_overdue = (
            sum(i["days"] for i in row["avg_overdue_list"]) / len(row["avg_overdue_list"])
            if row["avg_overdue_list"] else 0
        )

        avg_payment = (
            sum(i["days"] for i in row["avg_payment_list"]) / len(row["avg_payment_list"])
            if row["avg_payment_list"] else None
        )

        # ASM / RSM (ONLY from customer sales team)
        asm = None
        rsm = None
        for s in sales_map.get(cust, []):
            name = s.sales_person_name.lower()
            if "asm" in name:
                asm = s.sales_person
            if "rsm" in name:
                rsm = s.sales_person

        result.append({
            "customer_group": row["customer_group"],
            "customer": row["customer"],
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
