import frappe
from frappe.utils import today, getdate, date_diff


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {
            "label": "Distributor",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 220,
        },
        {
            "label": "Customer Group",
            "fieldname": "customer_group",
            "fieldtype": "Link",
            "options": "Customer Group",
            "width": 140,
        },
        {
            "label": "RSM",
            "fieldname": "rsm",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 140,
        },
        {
            "label": "ASM",
            "fieldname": "asm",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 140,
        },
        {
            "label": "TSO",
            "fieldname": "tso",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 140,
        },
        {
            "label": "Region",
            "fieldname": "region",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Territory",
            "fieldname": "territory",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Location",
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Total Outstanding",
            "fieldname": "total_outstanding",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "Total Overdue",
            "fieldname": "total_overdue",
            "fieldtype": "Currency",
            "width": 160,
        },
    ]


# --------------------------------------------------
# MAIN DATA
# --------------------------------------------------
def get_data(filters):

    customer_group = filters.get("customer_group")
    region_filter = filters.get("region")
    tso_filter = filters.get("tso")

    # ---------------- SALES PERSON MASTER ----------------
    sales_persons = frappe.db.sql("""
        SELECT
            name,
            parent_sales_person,
            custom_region,
            custom_territory,
            custom_location
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    sp_map = {}
    for sp in sales_persons:
        sp_map[sp.name] = sp

    # ---------------- CUSTOMER + SALES TEAM ----------------
    customers = frappe.db.sql("""
        SELECT
            c.name AS customer,
            c.customer_group,
            st.sales_person
        FROM `tabCustomer` c
        JOIN `tabSales Team` st
            ON st.parent = c.name
            AND st.parenttype = 'Customer'
        WHERE c.disabled = 0
          AND (%(customer_group)s IS NULL
               OR c.customer_group = %(customer_group)s)
    """, {
        "customer_group": customer_group
    }, as_dict=True)

    if not customers:
        return []

    # ---------------- OUTSTANDING ----------------
    invoices = frappe.db.sql("""
        SELECT
            customer,
            outstanding_amount,
            posting_date,
            due_date
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND outstanding_amount > 0
    """, as_dict=True)

    outstanding_map = {}
    overdue_map = {}

    for inv in invoices:
        outstanding_map.setdefault(inv.customer, 0)
        overdue_map.setdefault(inv.customer, 0)

        outstanding_map[inv.customer] += inv.outstanding_amount

        if inv.due_date and getdate(inv.due_date) < getdate(today()):
            overdue_map[inv.customer] += inv.outstanding_amount

    # ---------------- FINAL RESULT ----------------
    result = []

    for row in customers:

        tso = row.sales_person
        if tso not in sp_map:
            continue

        asm = sp_map[tso].parent_sales_person
        rsm = sp_map.get(asm, {}).get("parent_sales_person") if asm else None

        region = sp_map[tso].custom_region
        territory = sp_map[tso].custom_territory
        location = sp_map[tso].custom_location

        # Filters
        if region_filter and region != region_filter:
            continue

        if tso_filter and tso != tso_filter:
            continue

        result.append({
            "customer": row.customer,
            "customer_group": row.customer_group,
            "rsm": rsm,
            "asm": asm,
            "tso": tso,
            "region": region,
            "territory": territory,
            "location": location,
            "total_outstanding": outstanding_map.get(row.customer, 0),
            "total_overdue": overdue_map.get(row.customer, 0),
        })

    return result
