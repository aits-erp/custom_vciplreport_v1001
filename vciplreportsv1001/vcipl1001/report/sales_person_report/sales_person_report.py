import frappe
from frappe.utils import flt, getdate, add_years


def execute(filters=None):
    filters = frappe._dict(filters or {})
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {
            "label": "Head Sales Person",
            "fieldname": "head_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 190
        },
        {
            "label": "Head Sales Code",
            "fieldname": "custom_head_sales_code",
            "width": 150
        },
        {"label": "Region", "fieldname": "region", "width": 120},
        {"label": "Location", "fieldname": "location", "width": 150},
        {"label": "Territory", "fieldname": "territory", "width": 150},
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180
        },
        {"label": "Customer Name", "fieldname": "customer_name", "width": 240},
        {
            "label": "Target",
            "fieldname": "target",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": "Invoice Amount",
            "fieldname": "invoice_amount",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": "Last Year Achievement",
            "fieldname": "last_year_amount",
            "fieldtype": "Currency",
            "width": 180
        }
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    month = int(filters.get("month"))
    year = int(filters.get("year") or getdate(filters.from_date).year)

    from_date = getdate(filters.from_date)
    to_date = getdate(filters.to_date)

    ly_from = add_years(from_date, -1)
    ly_to = add_years(to_date, -1)

    # 🔹 FILTER VALUES
    f_region = filters.get("custom_region")
    f_parent = filters.get("parent_sales_person")
    f_customer = filters.get("customer")

    # ---------------- SALES PERSON MASTER ----------------
    sales_persons = frappe.db.sql("""
        SELECT
            name,
            parent_sales_person,
            custom_head_sales_code,
            custom_region,
            custom_location,
            custom_territory
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    sp_map = {sp.name: sp for sp in sales_persons}

    # ---------------- TARGET ----------------
    targets = frappe.db.sql("""
        SELECT
            st.sales_person,
            c.name AS customer,
            c.customer_name,
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
            END AS target
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE st.parenttype = 'Customer'
    """, {"month": month}, as_dict=True)

    # ---------------- CURRENT INVOICE ----------------
    current_invoice = frappe.db.sql("""
        SELECT
            customer,
            SUM(base_net_total) AS amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY customer
    """, {"f": from_date, "t": to_date}, as_dict=True)

    current_map = {r.customer: flt(r.amount) for r in current_invoice}

    # ---------------- LAST YEAR ----------------
    last_year_invoice = frappe.db.sql("""
        SELECT
            customer,
            SUM(base_net_total) AS amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY customer
    """, {"f": ly_from, "t": ly_to}, as_dict=True)

    last_year_map = {r.customer: flt(r.amount) for r in last_year_invoice}

    data = []
    total_target = 0
    total_invoice = 0

    for t in targets:
        sp = sp_map.get(t.sales_person)
        if not sp:
            continue

        head_sales_person = sp.parent_sales_person
        parent_sp = sp_map.get(head_sales_person)
        head_sales_code = parent_sp.custom_head_sales_code if parent_sp else None

        # ---------------- APPLY REGION FILTER ----------------
        if f_region and sp.custom_region != f_region:
            continue

        if f_parent and head_sales_person != f_parent:
            continue
        if f_customer and t.customer != f_customer:
            continue

        target_val = flt(t.target)
        invoice_val = current_map.get(t.customer, 0)

        total_target += target_val
        total_invoice += invoice_val

        data.append({
            "head_sales_person": head_sales_person,
            "custom_head_sales_code": head_sales_code,
            "region": sp.custom_region,
            "location": sp.custom_location,
            "territory": sp.custom_territory,
            "sales_person": t.sales_person,
            "customer_name": t.customer_name,
            "target": target_val,
            "invoice_amount": invoice_val,
            "last_year_amount": last_year_map.get(t.customer, 0),
        })

    # ---------------- TOTAL ROW ----------------
    if data:
        data.append({
            "customer_name": "TOTAL",
            "target": total_target,
            "invoice_amount": total_invoice
        })

    return data
