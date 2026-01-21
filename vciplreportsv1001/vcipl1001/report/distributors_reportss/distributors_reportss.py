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
        {"label": "Region", "fieldname": "region", "width": 140},
        {"label": "Location", "fieldname": "location", "width": 160},
        {"label": "Territory", "fieldname": "territory", "width": 160},
        {
            "label": "Parent Sales Person",
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180,
        },
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180,
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 220,
        },
        {
            "label": "Target",
            "fieldname": "target",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": "Invoice Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "Last Year Achievement",
            "fieldname": "last_year_amount",
            "fieldtype": "Currency",
            "width": 180,
        },
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    # ---------------- DATE LOGIC ----------------
    from_date = getdate(filters.from_date)
    to_date = getdate(filters.to_date)

    ly_from_date = add_years(from_date, -1)
    ly_to_date = add_years(to_date, -1)

    month = int(filters.month or from_date.month)

    # ---------------- OPTIONAL FILTERS ----------------
    f_region = filters.get("custom_region")
    f_location = filters.get("custom_location")
    f_territory = filters.get("custom_territory")
    f_parent = filters.get("parent_sales_person")
    f_customer = filters.get("customer")

    # ---------------- SALES PERSON MASTER ----------------
    sales_persons = frappe.db.sql("""
        SELECT
            name,
            parent_sales_person,
            custom_region,
            custom_location,
            custom_territory
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    sp_map = {sp.name: sp for sp in sales_persons}

    # ---------------- TARGET (MONTH-WISE) ----------------
    targets = frappe.db.sql("""
        SELECT
            st.sales_person,
            c.name AS customer,
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

    # ---------------- CURRENT YEAR INVOICE ----------------
    current_rows = frappe.db.sql("""
        SELECT
            customer,
            SUM(base_net_total) AS amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from)s AND %(to)s
        GROUP BY customer
    """, {"from": from_date, "to": to_date}, as_dict=True)

    current_map = {r.customer: flt(r.amount) for r in current_rows}

    # ---------------- LAST YEAR INVOICE ----------------
    last_year_rows = frappe.db.sql("""
        SELECT
            customer,
            SUM(base_net_total) AS amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from)s AND %(to)s
        GROUP BY customer
    """, {"from": ly_from_date, "to": ly_to_date}, as_dict=True)

    last_year_map = {r.customer: flt(r.amount) for r in last_year_rows}

    # ---------------- FINAL DATA ----------------
    data = []

    for t in targets:
        sp = sp_map.get(t.sales_person)
        if not sp:
            continue

        # TREE-LIKE FILTERING
        if f_region and sp.custom_region != f_region:
            continue
        if f_location and sp.custom_location != f_location:
            continue
        if f_territory and sp.custom_territory != f_territory:
            continue
        if f_parent and sp.parent_sales_person != f_parent:
            continue
        if f_customer and t.customer != f_customer:
            continue

        data.append({
            "region": sp.custom_region,
            "location": sp.custom_location,
            "territory": sp.custom_territory,
            "parent_sales_person": sp.parent_sales_person,
            "sales_person": t.sales_person,
            "customer": t.customer,  # ✅ CUSTOMER NAME ONLY
            "target": flt(t.target),
            "amount": current_map.get(t.customer, 0),
            "last_year_amount": last_year_map.get(t.customer, 0),
        })

    return data
