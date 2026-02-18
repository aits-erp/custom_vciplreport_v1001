# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate, cint

def execute(filters=None):
    """
    Main function to execute the report
    """
    filters = frappe._dict(filters or {})
    set_default_filters(filters)
    
    columns = get_columns(filters)
    data = get_data(filters)
    
    return columns, data


def set_default_filters(filters):
    """
    Set default values for filters if not provided
    """
    today = nowdate()
    
    if not filters.get("year"):
        filters.year = cint(today[:4])
    else:
        filters.year = cint(filters.year)
    
    if not filters.get("month"):
        filters.month = cint(today[5:7])
    else:
        filters.month = cint(filters.month)
    
    # Set date range for the selected month
    filters.from_date = get_first_day(f"{filters.year}-{filters.month:02d}-01")
    filters.to_date = get_last_day(f"{filters.year}-{filters.month:02d}-01")
    
    # Set previous year same month dates
    if filters.get("compare_previous_year"):
        filters.ly_from_date = add_years(filters.from_date, -1)
        filters.ly_to_date = add_years(filters.to_date, -1)
    
    # Default values for other filters
    if not filters.get("include_targets"):
        filters.include_targets = 1


def get_columns(filters):
    """
    Return columns for the report
    """
    columns = [
        {
            "label": _("Level"),
            "fieldname": "level",
            "fieldtype": "Data",
            "width": 60,
            "hidden": 1
        },
        {
            "label": _("Head Sales Person"),
            "fieldname": "head_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180
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
            "width": 250
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
        {
            "label": _("Territory Name"),
            "fieldname": "territory_name",
            "fieldtype": "Data",
            "width": 140
        }
    ]
    
    # Add target columns if include_targets is enabled
    if filters.include_targets:
        columns.extend([
            {
                "label": _(f"Target ({get_month_name(filters.month)})"),
                "fieldname": "monthly_target",
                "fieldtype": "Currency",
                "width": 140
            }
        ])
    
    # Invoice columns
    columns.extend([
        {
            "label": _(f"Invoice Amount ({get_month_name(filters.month)})"),
            "fieldname": "invoice_amount",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": _("Achieved %"),
            "fieldname": "achieved_pct",
            "fieldtype": "Percent",
            "width": 120
        }
    ])
    
    # Add previous year comparison if enabled
    if filters.get("compare_previous_year"):
        columns.extend([
            {
                "label": _(f"Last Year ({get_month_name(filters.month)})"),
                "fieldname": "last_year_amount",
                "fieldtype": "Currency",
                "width": 160
            },
            {
                "label": _("Growth %"),
                "fieldname": "growth_pct",
                "fieldtype": "Percent",
                "width": 120
            }
        ])
    
    # Add indent for tree view
    columns.append({
        "fieldname": "indent",
        "fieldtype": "Data",
        "hidden": 1
    })
    
    columns.append({
        "fieldname": "is_total_row",
        "fieldtype": "Data",
        "hidden": 1
    })
    
    return columns


def get_month_name(month):
    """
    Get month name from month number
    """
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    return month_names.get(month, "")


def get_data(filters):
    """
    Main function to fetch and process data
    """
    data = []
    
    # Add header
    data.append({
        "level": "1",
        "customer_name": "<b>SALES PERSON PERFORMANCE</b>",
        "indent": 0
    })
    
    # Get sales persons with their details
    sales_persons = get_sales_persons(filters)
    
    if not sales_persons:
        frappe.msgprint(_("No sales persons found with the selected filters"))
        return data
    
    # Get targets
    targets = get_targets(filters, sales_persons) if filters.include_targets else {}
    
    # Get invoice data
    invoices = get_invoice_data(filters)
    
    # Get previous year data if enabled
    last_year_data = {}
    if filters.get("compare_previous_year"):
        last_year_data = get_previous_year_data(filters)
    
    # Track totals
    grand_total_target = 0
    grand_total_invoice = 0
    grand_total_last_year = 0
    
    # Process each sales person
    for sp in sales_persons:
        # Get customers for this sales person
        customers = get_customers_for_sales_person(sp.name, filters)
        
        if not customers:
            continue
        
        sp_total_target = 0
        sp_total_invoice = 0
        sp_total_last_year = 0
        
        # Add each customer
        for customer in customers:
            # Get targets
            monthly_target = 0
            if filters.include_targets:
                sp_targets = targets.get(sp.name, {})
                monthly_target = sp_targets.get(customer.customer, 0)
            
            # Get invoice data
            sp_invoices = invoices.get(sp.name, {})
            customer_invoice = sp_invoices.get(customer.customer, {})
            invoice_amount = customer_invoice.get("amount", 0)
            
            # Get last year data
            last_year_amount = 0
            if filters.get("compare_previous_year"):
                sp_ly = last_year_data.get(sp.name, {})
                last_year_amount = sp_ly.get(customer.customer, 0)
            
            # Calculate achievement
            achieved_pct = (invoice_amount / monthly_target * 100) if monthly_target else 0
            
            # Calculate growth
            growth_pct = 0
            if last_year_amount:
                growth_pct = ((invoice_amount - last_year_amount) / last_year_amount * 100)
            
            # Add customer row
            row = {
                "level": "2",
                "head_sales_person": sp.parent_sales_person,
                "sales_person": sp.name,
                "customer_name": customer.customer_name,
                "region": sp.region,
                "location": sp.location,
                "territory_name": sp.territory_name,
                "monthly_target": monthly_target,
                "invoice_amount": invoice_amount,
                "achieved_pct": achieved_pct,
                "indent": 1
            }
            
            if filters.get("compare_previous_year"):
                row["last_year_amount"] = last_year_amount
                row["growth_pct"] = growth_pct
            
            data.append(row)
            
            # Add to totals
            sp_total_target += monthly_target
            sp_total_invoice += invoice_amount
            sp_total_last_year += last_year_amount
        
        # Add sales person total row
        if sp_total_invoice > 0 or sp_total_target > 0:
            sp_achieved = (sp_total_invoice / sp_total_target * 100) if sp_total_target else 0
            sp_growth = ((sp_total_invoice - sp_total_last_year) / sp_total_last_year * 100) if sp_total_last_year else 0
            
            total_row = {
                "level": "2",
                "customer_name": f"<b>TOTAL - {sp.sales_person_name or sp.name}</b>",
                "monthly_target": sp_total_target,
                "invoice_amount": sp_total_invoice,
                "achieved_pct": sp_achieved,
                "indent": 1,
                "is_total_row": 1
            }
            
            if filters.get("compare_previous_year"):
                total_row["last_year_amount"] = sp_total_last_year
                total_row["growth_pct"] = sp_growth
            
            data.append(total_row)
            
            # Add to grand totals
            grand_total_target += sp_total_target
            grand_total_invoice += sp_total_invoice
            grand_total_last_year += sp_total_last_year
    
    # Add grand total row
    if grand_total_invoice > 0 or grand_total_target > 0:
        grand_achieved = (grand_total_invoice / grand_total_target * 100) if grand_total_target else 0
        grand_growth = ((grand_total_invoice - grand_total_last_year) / grand_total_last_year * 100) if grand_total_last_year else 0
        
        grand_total_row = {
            "level": "1",
            "customer_name": "<b>GRAND TOTAL</b>",
            "monthly_target": grand_total_target,
            "invoice_amount": grand_total_invoice,
            "achieved_pct": grand_achieved,
            "indent": 0,
            "is_total_row": 1
        }
        
        if filters.get("compare_previous_year"):
            grand_total_row["last_year_amount"] = grand_total_last_year
            grand_total_row["growth_pct"] = grand_growth
        
        data.append(grand_total_row)
    
    return data


def get_sales_persons(filters):
    """
    Fetch sales persons based on filters
    """
    conditions = ["enabled = 1"]
    values = {}
    
    if filters.get("parent_sales_person"):
        conditions.append("parent_sales_person = %(parent_sales_person)s")
        values["parent_sales_person"] = filters.parent_sales_person
    
    if filters.get("sales_person"):
        conditions.append("name = %(sales_person)s")
        values["sales_person"] = filters.sales_person
    
    if filters.get("custom_region"):
        conditions.append("custom_region = %(custom_region)s")
        values["custom_region"] = filters.custom_region
    
    if filters.get("custom_location"):
        conditions.append("custom_location = %(custom_location)s")
        values["custom_location"] = filters.custom_location
    
    if filters.get("custom_territory_name"):
        conditions.append("custom_territory_name = %(custom_territory_name)s")
        values["custom_territory_name"] = filters.custom_territory_name
    
    where_clause = " AND ".join(conditions)
    
    return frappe.db.sql(f"""
        SELECT 
            name,
            sales_person_name,
            parent_sales_person,
            custom_region as region,
            custom_location as location,
            custom_territory_name as territory_name
        FROM `tabSales Person`
        WHERE {where_clause}
        ORDER BY parent_sales_person, name
    """, values, as_dict=True)


def get_targets(filters, sales_persons):
    """
    Fetch targets for sales persons
    """
    if not filters.include_targets:
        return {}
    
    sp_names = [sp.name for sp in sales_persons]
    if not sp_names:
        return {}
    
    month_field = get_month_field(filters.month)
    
    targets = frappe.db.sql(f"""
        SELECT 
            sales_person,
            parent as customer,
            {month_field} as monthly_target
        FROM `tabSales Team`
        WHERE parenttype = 'Customer'
            AND sales_person IN %(sp_names)s
    """, {
        "sp_names": sp_names
    }, as_dict=True)
    
    # Organize targets by sales person and customer
    target_dict = {}
    for t in targets:
        if t.sales_person not in target_dict:
            target_dict[t.sales_person] = {}
        target_dict[t.sales_person][t.customer] = flt(t.monthly_target)
    
    return target_dict


def get_month_field(month):
    """
    Get the field name for a given month
    """
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
        12: "custom_december"
    }
    return month_fields.get(month, "custom_january")


def get_invoice_data(filters):
    """
    Fetch invoice data for the selected period
    """
    conditions = [
        "si.docstatus = 1",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    ]
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }
    
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.customer
    
    invoices = frappe.db.sql(f"""
        SELECT 
            si.customer,
            st.sales_person,
            SUM(si.base_net_total) as total_amount
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        WHERE {" AND ".join(conditions)}
        GROUP BY si.customer, st.sales_person
    """, values, as_dict=True)
    
    # Organize by sales person and customer
    invoice_dict = {}
    for inv in invoices:
        if not inv.sales_person:
            continue
        
        if inv.sales_person not in invoice_dict:
            invoice_dict[inv.sales_person] = {}
        
        invoice_dict[inv.sales_person][inv.customer] = {
            "amount": flt(inv.total_amount)
        }
    
    return invoice_dict


def get_previous_year_data(filters):
    """
    Fetch previous year data for comparison
    """
    if not filters.get("ly_from_date") or not filters.get("ly_to_date"):
        return {}
    
    data = frappe.db.sql("""
        SELECT 
            si.customer,
            st.sales_person,
            SUM(si.base_net_total) as amount
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY si.customer, st.sales_person
    """, {
        "from_date": filters.ly_from_date,
        "to_date": filters.ly_to_date
    }, as_dict=True)
    
    # Organize by sales person and customer
    result = {}
    for d in data:
        if not d.sales_person:
            continue
        
        if d.sales_person not in result:
            result[d.sales_person] = {}
        
        result[d.sales_person][d.customer] = flt(d.amount)
    
    return result


def get_customers_for_sales_person(sales_person, filters):
    """
    Get customers assigned to a sales person
    """
    conditions = ["parenttype = 'Customer'", "sales_person = %(sales_person)s"]
    values = {"sales_person": sales_person}
    
    if filters.get("customer"):
        conditions.append("parent = %(customer)s")
        values["customer"] = filters.customer
    
    where_clause = " AND ".join(conditions)
    
    customers = frappe.db.sql(f"""
        SELECT 
            st.parent as customer,
            c.customer_name
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE {where_clause}
        ORDER BY c.customer_name
    """, values, as_dict=True)
    
    return customers
