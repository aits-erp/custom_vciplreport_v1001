# Copyright (c) 2024, your company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate, getdate


def execute(filters=None):
    """
    Main execute function - required entry point for Frappe reports
    """
    filters = frappe._dict(filters or {})
    set_default_filters(filters)
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data


def set_default_filters(filters):
    """Set default values for filters if not provided"""
    today = nowdate()
    year = int(today[:4])
    month = int(today[5:7])

    filters.period_type = filters.get("period_type") or "Month"
    filters.year = int(filters.get("year") or year)
    filters.month = int(filters.get("month") or month)
    filters.quarter = filters.get("quarter") or "Q1"
    filters.half_year = filters.get("half_year") or "H1"


def get_columns():
    """Define report columns with Territory Code added"""
    return [
        {
            "label": _("Head Sales Person"),
            "fieldname": "head_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180
        },
        {
            "label": _("Head Sales Code"),
            "fieldname": "custom_head_sales_code",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Region"),
            "fieldname": "region",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Location"),
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 150
        },
        # NEW COLUMN: Territory Code (before Territory Name)
        {
            "label": _("Territory Code"),
            "fieldname": "custom_territory",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Territory Name"),
            "fieldname": "custom_territory_name",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": _("Target"),
            "fieldname": "target",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": _("Invoice Amount"),
            "fieldname": "invoice_amount",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Achieved %"),
            "fieldname": "achieved_pct",
            "fieldtype": "Percent",
            "width": 140
        },
        {
            "label": _("Last Year Achievement"),
            "fieldname": "last_year_amount",
            "fieldtype": "Currency",
            "width": 170
        },
        # Hidden columns for drill down data
        {
            "label": _("From Date"),
            "fieldname": "from_date",
            "fieldtype": "Date",
            "hidden": 1
        },
        {
            "label": _("To Date"),
            "fieldname": "to_date",
            "fieldtype": "Date",
            "hidden": 1
        }
    ]


def get_months(filters):
    """Get months based on period type selection"""
    if filters.period_type == "Quarter":
        q_map = {
            "Q1": [4, 5, 6],    # Apr-Jun
            "Q2": [7, 8, 9],    # Jul-Sep
            "Q3": [10, 11, 12], # Oct-Dec
            "Q4": [1, 2, 3],    # Jan-Mar
        }
        return q_map.get(filters.quarter, [4, 5, 6])

    if filters.period_type == "Half Year":
        return [4, 5, 6, 7, 8, 9] if filters.half_year == "H1" else [10, 11, 12, 1, 2, 3]

    return [int(filters.month)]


def get_date_range(filters):
    """Get from_date and to_date based on selected period"""
    months = get_months(filters)
    year = int(filters.year)
    
    # Handle year transition for periods crossing calendar year
    if max(months) < min(months):  # Period crosses year boundary (e.g., Oct-Mar)
        from_date = get_first_day(f"{year}-{months[0]}-01")
        to_date = get_last_day(f"{year + 1}-{months[-1]}-01")
    else:
        from_date = get_first_day(f"{year}-{months[0]}-01")
        to_date = get_last_day(f"{year}-{months[-1]}-01")
    
    return from_date, to_date


def get_data(filters):
    """Main function to fetch and process report data"""
    # Get date ranges
    from_date, to_date = get_date_range(filters)
    
    # Get last year's dates for comparison
    ly_from = add_years(from_date, -1)
    ly_to = add_years(to_date, -1)

    # Get filter values
    f_region = filters.get("custom_region")
    f_location = filters.get("custom_location")
    f_territory = filters.get("custom_territory_name")
    f_parent = filters.get("parent_sales_person")
    f_customer = filters.get("customer")

    # Get all enabled sales persons with territory code
    sales_persons = frappe.db.sql("""
        SELECT 
            name, 
            parent_sales_person, 
            custom_head_sales_code,
            custom_region, 
            custom_location, 
            custom_territory_name,
            custom_territory
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

    sp_map = {sp.name: sp for sp in sales_persons}

    # Month field mapping for target amounts
    month_fields = {
        1: "custom_january", 
        2: "custom_february", 
        3: "custom_march",
        4: "custom_april", 
        5: "custom_may_", 
        6: "custom_june",
        7: "custom_july", 
        8: "custom_august", 
        9: "custom_september",
        10: "custom_october", 
        11: "custom_november", 
        12: "custom_december",
    }

    # Get selected months and build target sum expression
    months = get_months(filters)
    target_fields = [f"COALESCE(st.{month_fields[m]},0)" for m in months]
    target_expr = " + ".join(target_fields)

    # Fetch targets from Sales Team linked to Customers
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

    # Fetch current year invoices
    invoices = frappe.db.sql("""
        SELECT 
            customer, 
            SUM(base_net_total) as amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY customer
    """, {
        "from_date": from_date, 
        "to_date": to_date
    }, as_dict=True)

    invoice_map = {i.customer: flt(i.amount) for i in invoices}

    # Fetch last year invoices
    last_year = frappe.db.sql("""
        SELECT 
            customer, 
            SUM(base_net_total) as amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY customer
    """, {
        "from_date": ly_from, 
        "to_date": ly_to
    }, as_dict=True)

    last_year_map = {i.customer: flt(i.amount) for i in last_year}

    # Build report data
    data = []
    total_target = 0
    total_invoice = 0

    for t in targets:
        sp = sp_map.get(t.sales_person)
        if not sp:
            continue

        # Apply filters
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

        # Get parent sales person details
        parent_sp = sp_map.get(sp.parent_sales_person)

        target = flt(t.target)
        invoice = invoice_map.get(t.customer, 0)
        achieved_pct = (invoice / target * 100) if target else 0

        # Only include records with target or invoice
        if target > 0 or invoice > 0:
            total_target += target
            total_invoice += invoice

            data.append({
                "head_sales_person": sp.parent_sales_person,
                "custom_head_sales_code": parent_sp.custom_head_sales_code if parent_sp else None,
                "region": sp.custom_region,
                "location": sp.custom_location,
                "custom_territory": sp.custom_territory,
                "custom_territory_name": sp.custom_territory_name,
                "sales_person": t.sales_person,
                "customer_name": t.customer_name,
                "target": target,
                "invoice_amount": invoice,
                "achieved_pct": round(achieved_pct, 2),
                "last_year_amount": last_year_map.get(t.customer, 0),
                "from_date": from_date,
                "to_date": to_date
            })

    # Add total row
    if data:
        total_achieved_pct = (total_invoice / total_target * 100) if total_target else 0
        data.append({
            "customer_name": "<b>TOTAL</b>",
            "target": total_target,
            "invoice_amount": total_invoice,
            "achieved_pct": round(total_achieved_pct, 2)
        })

    return data


@frappe.whitelist()
def get_invoice_details(customer, sales_person=None, from_date=None, to_date=None):
    """
    Fetch invoice details for drill down
    This method is called when clicking on invoice amount
    """
    try:
        # Build query conditions
        conditions = ["si.docstatus = 1", "si.customer = %(customer)s"]
        params = {"customer": customer}
        
        if from_date and to_date:
            conditions.append("si.posting_date BETWEEN %(from_date)s AND %(to_date)s")
            params["from_date"] = from_date
            params["to_date"] = to_date
        
        # If sales person filter is applied, join with Sales Team
        if sales_person:
            conditions.append("""
                EXISTS (
                    SELECT 1 
                    FROM `tabSales Team` st 
                    WHERE st.parent = si.name 
                        AND st.parenttype = 'Sales Invoice' 
                        AND st.sales_person = %(sales_person)s
                )
            """)
            params["sales_person"] = sales_person
        
        where_clause = " AND ".join(conditions)
        
        # Fetch invoice details
        query = f"""
            SELECT 
                si.name,
                si.posting_date,
                si.customer,
                si.base_net_total as amount,
                si.currency,
                si.status
            FROM `tabSales Invoice` si
            WHERE {where_clause}
            ORDER BY si.posting_date DESC
        """
        
        invoices = frappe.db.sql(query, params, as_dict=True)
        
        # Format amounts
        for inv in invoices:
            inv.amount = flt(inv.amount)
        
        return invoices
        
    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Sales Person Report - Invoice Details Error"
        )
        return {"error": str(e)}