import frappe
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    set_default_filters(filters)
    return get_columns(), get_data(filters)


# --------------------------------------------------
# DEFAULT FILTERS
# --------------------------------------------------
def set_default_filters(filters):
    today = nowdate()
    year = int(today[:4])
    month = int(today[5:7])

    filters.period_type = filters.get("period_type") or "Month"
    filters.year = int(filters.get("year") or year)
    filters.month = int(filters.get("month") or month)
    filters.quarter = filters.get("quarter") or "Q1"
    filters.half_year = filters.get("half_year") or "H1"


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "Head Sales Person", "fieldname": "head_sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Head Sales Code", "fieldname": "custom_head_sales_code", "width": 140},
        {"label": "Region", "fieldname": "region", "width": 120},
        {"label": "Location", "fieldname": "location", "width": 150},
        {"label": "Territory", "fieldname": "custom_territory_name", "width": 140},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Customer Name", "fieldname": "customer_name", "width": 220},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 130},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved Target %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 140},
        {"label": "Last Year Achievement", "fieldname": "last_year_amount", "fieldtype": "Currency", "width": 170},
    ]


# --------------------------------------------------
# FINANCIAL YEAR MONTH MAPPING
# --------------------------------------------------
def get_months(filters):
    if filters.period_type == "Quarter":
        q_map = {
            "Q1": [4, 5, 6],
            "Q2": [7, 8, 9],
            "Q3": [10, 11, 12],
            "Q4": [1, 2, 3],
        }
        return q_map.get(filters.quarter, [4, 5, 6])

    if filters.period_type == "Half Year":
        return [4, 5, 6, 7, 8, 9] if filters.half_year == "H1" else [10, 11, 12, 1, 2, 3]

    return [int(filters.month)]


# --------------------------------------------------
# DATE RANGE
# --------------------------------------------------
def get_date_range(filters):
    months = get_months(filters)
    year = int(filters.year)

    from_date = get_first_day(f"{year}-{months[0]}-01")
    to_date = get_last_day(f"{year}-{months[-1]}-01")

    return from_date, to_date


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters):

    from_date, to_date = get_date_range(filters)

    ly_from = add_years(from_date, -1)
    ly_to = add_years(to_date, -1)

    f_region = filters.get("custom_region")
    f_location = filters.get("custom_location")
    f_territory = filters.get("custom_territory_name")
    f_parent = filters.get("parent_sales_person")
    f_customer = filters.get("customer")

    sales_persons = frappe.db.sql("""
        SELECT name, parent_sales_person, custom_head_sales_code,
               custom_region, custom_location, custom_territory_name
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    sp_map = {sp.name: sp for sp in sales_persons}

    month_fields = {
        1: "custom_january", 2: "custom_february", 3: "custom_march",
        4: "custom_april", 5: "custom_may_", 6: "custom_june",
        7: "custom_july", 8: "custom_august", 9: "custom_september",
        10: "custom_october", 11: "custom_november", 12: "custom_december",
    }

    months = get_months(filters)
    target_expr = " + ".join([f"COALESCE(st.{month_fields[m]},0)" for m in months])

    targets = frappe.db.sql(f"""
        SELECT
            st.sales_person,
            c.name AS customer,
            c.customer_name,
            ({target_expr}) AS target
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE st.parenttype = 'Customer'
    """, as_dict=True)

    invoices = frappe.db.sql("""
        SELECT customer, SUM(base_net_total) amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY customer
    """, {"f": from_date, "t": to_date}, as_dict=True)

    invoice_map = {i.customer: flt(i.amount) for i in invoices}

    last_year = frappe.db.sql("""
        SELECT customer, SUM(base_net_total) amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY customer
    """, {"f": ly_from, "t": ly_to}, as_dict=True)

    last_year_map = {i.customer: flt(i.amount) for i in last_year}

    data = []
    total_target = total_invoice = 0

    for t in targets:
        sp = sp_map.get(t.sales_person)
        if not sp:
            continue

        if f_region and sp.custom_region != f_region:
            continue
        if f_location and sp.custom_location != f_location:
            continue
        if f_territory and sp.custom_territory_name != f_territory:
            continue
        if f_parent and sp.parent_sales_person != f_parent:
            continue
        if f_customer and t.customer != f_customer:
            continue

        parent_sp = sp_map.get(sp.parent_sales_person)

        target = flt(t.target)
        invoice = invoice_map.get(t.customer, 0)
        achieved_pct = (invoice / target * 100) if target else 0

        total_target += target
        total_invoice += invoice

        data.append({
            "head_sales_person": sp.parent_sales_person,
            "custom_head_sales_code": parent_sp.custom_head_sales_code if parent_sp else None,
            "region": sp.custom_region,
            "location": sp.custom_location,
            "custom_territory_name": sp.custom_territory_name,
            "sales_person": t.sales_person,
            "customer_name": t.customer_name,
            "target": target,
            "invoice_amount": invoice,
            "achieved_pct": achieved_pct,
            "last_year_amount": last_year_map.get(t.customer, 0),
        })

    if data:
        data.append({
            "customer_name": "TOTAL",
            "target": total_target,
            "invoice_amount": total_invoice,
            "achieved_pct": (total_invoice / total_target * 100) if total_target else 0,
        })

    return data
