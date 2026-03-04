// frappe.query_reports["Sales Person Report"] = {
//     filters: [
//         // ---------------- PERIOD TYPE ----------------
//         {
//             fieldname: "period_type",
//             label: "Period Type",
//             fieldtype: "Select",
//             options: ["Month", "Quarter", "Half Year"],
//             default: "Month",
//             reqd: 1
//         },

//         // ---------------- MONTH ----------------
//         {
//             fieldname: "month",
//             label: "Month",
//             fieldtype: "Select",
//             options: [
//                 { label: "January", value: 1 },
//                 { label: "February", value: 2 },
//                 { label: "March", value: 3 },
//                 { label: "April", value: 4 },
//                 { label: "May", value: 5 },
//                 { label: "June", value: 6 },
//                 { label: "July", value: 7 },
//                 { label: "August", value: 8 },
//                 { label: "September", value: 9 },
//                 { label: "October", value: 10 },
//                 { label: "November", value: 11 },
//                 { label: "December", value: 12 }
//             ],
//             default: new Date().getMonth() + 1,
//             depends_on: "eval:doc.period_type=='Month'"
//         },

//         // ---------------- QUARTER (FY STYLE) ----------------
//         {
//             fieldname: "quarter",
//             label: "Quarter",
//             fieldtype: "Select",
//             options: [
//                 { label: "Q1 (Apr–Jun)", value: "Q1" },
//                 { label: "Q2 (Jul–Sep)", value: "Q2" },
//                 { label: "Q3 (Oct–Dec)", value: "Q3" },
//                 { label: "Q4 (Jan–Mar)", value: "Q4" }
//             ],
//             default: "Q1",
//             depends_on: "eval:doc.period_type=='Quarter'"
//         },

//         // ---------------- HALF YEAR ----------------
//         {
//             fieldname: "half_year",
//             label: "Half Year",
//             fieldtype: "Select",
//             options: [
//                 { label: "H1 (Apr–Sep)", value: "H1" },
//                 { label: "H2 (Oct–Mar)", value: "H2" }
//             ],
//             default: "H1",
//             depends_on: "eval:doc.period_type=='Half Year'"
//         },

//         // ---------------- YEAR ----------------
//         {
//             fieldname: "year",
//             label: "Year",
//             fieldtype: "Select",
//             options: ["2023", "2024", "2025", "2026"],
//             default: new Date().getFullYear().toString(),
//             reqd: 1
//         },

//         // ---------------- REGION ----------------
//         {
//             fieldname: "custom_region",
//             label: "Region",
//             fieldtype: "Data"
//         },

//         // ---------------- LOCATION ----------------
//         {
//             fieldname: "custom_location",
//             label: "Location",
//             fieldtype: "Data"
//         },

//         // ---------------- TERRITORY (updated fieldname) ----------------
//         {
//             fieldname: "custom_territory_name",
//             label: "Territory",
//             fieldtype: "Data"
//         },

//         // ---------------- HEAD SALES PERSON ----------------
//         {
//             fieldname: "parent_sales_person",
//             label: "Head Sales Person",
//             fieldtype: "Link",
//             options: "Sales Person"
//         },

//         // ---------------- CUSTOMER ----------------
//         {
//             fieldname: "customer",
//             label: "Customer",
//             fieldtype: "Link",
//             options: "Customer"
//         }
//     ]
// };

// Copyright (c) 2024, your company and contributors
// For license information, please see license.txt
# Copyright (c) 2024, your company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate, getdate
import json


def execute(filters=None):
    """
    Main execute function - required entry point for Frappe reports
    """
    if not filters:
        filters = {}
    
    filters = frappe._dict(filters or {})
    set_default_filters(filters)
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data


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
# COLUMNS - ADDED TERRITORY CODE COLUMN
# --------------------------------------------------
def get_columns():
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


# --------------------------------------------------
# FINANCIAL YEAR MONTH MAPPING
# --------------------------------------------------
def get_months(filters):
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


# --------------------------------------------------
# DATE RANGE
# --------------------------------------------------
def get_date_range(filters):
    months = get_months(filters)
    year = int(filters.year)
    
    # Handle year transition for periods crossing calendar year
    if max(months) < min(months):  # Period crosses year boundary (e.g., Oct-Mar)
        # First part of period (Oct-Dec) in current year
        from_date = get_first_day(f"{year}-{months[0]}-01")
        
        # Last part of period (Jan-Mar) in next year
        to_date = get_last_day(f"{year + 1}-{months[-1]}-01")
    else:
        from_date = get_first_day(f"{year}-{months[0]}-01")
        to_date = get_last_day(f"{year}-{months[-1]}-01")
    
    return from_date, to_date


# --------------------------------------------------
# DATA - UPDATED TO INCLUDE TERRITORY CODE
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

    # UPDATED: Added custom_territory to the SELECT query
    sales_persons = frappe.db.sql("""
        SELECT 
            name, 
            parent_sales_person, 
            custom_head_sales_code,
            custom_region, 
            custom_location, 
            custom_territory_name,
            custom_territory  /* Added territory code field */
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

        # UPDATED: Added custom_territory to the data dictionary
        data.append({
            "head_sales_person": sp.parent_sales_person,
            "custom_head_sales_code": parent_sp.custom_head_sales_code if parent_sp else None,
            "region": sp.custom_region,
            "location": sp.custom_location,
            "custom_territory": sp.custom_territory,  # Added territory code
            "custom_territory_name": sp.custom_territory_name,
            "sales_person": t.sales_person,
            "customer_name": t.customer_name,
            "target": target,
            "invoice_amount": invoice,
            "achieved_pct": round(achieved_pct, 2),
            "last_year_amount": last_year_map.get(t.customer, 0),
            "from_date": from_date,  # For drill down
            "to_date": to_date        # For drill down
        })

    if data:
        total_achieved_pct = (total_invoice / total_target * 100) if total_target else 0
        data.append({
            "customer_name": "<b>TOTAL</b>",
            "target": total_target,
            "invoice_amount": total_invoice,
            "achieved_pct": round(total_achieved_pct, 2),
            "indent": 0,
            "bold": 1
        })

    return data


# --------------------------------------------------
# INVOICE DETAILS FOR DRILL DOWN
# --------------------------------------------------
@frappe.whitelist()
def get_invoice_details(customer, sales_person=None, from_date=None, to_date=None):
    """
    Fetch invoice details for drill down
    This method is called when clicking on invoice amount
    """
    try:
        # Parse dates if they're strings
        if from_date and isinstance(from_date, str):
            from_date = from_date
        if to_date and isinstance(to_date, str):
            to_date = to_date
        
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
                si.status,
                si.remarks
            FROM `tabSales Invoice` si
            WHERE {where_clause}
            ORDER BY si.posting_date DESC
        """
        
        invoices = frappe.db.sql(query, params, as_dict=True)
        
        # Format amounts
        for inv in invoices:
            inv.amount = flt(inv.amount)
            # Add formatted date for display
            inv.posting_date = getdate(inv.posting_date).strftime('%Y-%m-%d')
        
        return invoices
        
    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Sales Person Report - Invoice Details Error"
        )
        return {"error": str(e)}
