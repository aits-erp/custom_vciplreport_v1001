# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate, cint
import json
from calendar import monthrange

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
    
    if not filters.get("detailed_view"):
        filters.detailed_view = 0


def get_columns(filters):
    """
    Return columns for the report
    """
    columns = [
        {
            "label": _("Head Sales Person"),
            "fieldname": "head_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180
        },
        {
            "label": _("Head Sales Code"),
            "fieldname": "head_sales_code",
            "fieldtype": "Data",
            "width": 120
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
            "label": _("Territory"),
            "fieldname": "territory",
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
            "label": _("Sales Person Code"),
            "fieldname": "sales_person_code",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": _("Customer Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 150
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
            },
            {
                "label": _("Quarterly Target"),
                "fieldname": "quarterly_target",
                "fieldtype": "Currency",
                "width": 140
            },
            {
                "label": _("Yearly Target"),
                "fieldname": "yearly_target",
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
    
    # Add additional columns for detailed view
    if filters.detailed_view:
        columns.extend([
            {
                "label": _("Total Qty"),
                "fieldname": "total_qty",
                "fieldtype": "Float",
                "width": 120
            },
            {
                "label": _("No. of Invoices"),
                "fieldname": "invoice_count",
                "fieldtype": "Int",
                "width": 130
            },
            {
                "label": _("Average Invoice Value"),
                "fieldname": "avg_invoice_value",
                "fieldtype": "Currency",
                "width": 160
            }
        ])
    
    return columns


def get_data(filters):
    """
    Main function to fetch and process data
    """
    # Get all active sales persons
    sales_persons = get_sales_persons(filters)
    
    # Get targets for sales persons
    targets = get_targets(filters, sales_persons)
    
    # Get invoice data
    invoices = get_invoice_data(filters)
    
    # Get previous year data if enabled
    last_year_data = {}
    if filters.get("compare_previous_year"):
        last_year_data = get_previous_year_data(filters)
    
    # Build the data structure
    data = []
    
    # Group by head sales person
    head_sales_persons = {}
    for sp in sales_persons:
        head = sp.get("parent_sales_person") or "No Head"
        if head not in head_sales_persons:
            head_sales_persons[head] = []
        head_sales_persons[head].append(sp)
    
    # Process data for each head sales person
    for head_name, sp_list in head_sales_persons.items():
        # Add head row
        head_row = get_head_summary(head_name, sp_list, targets, invoices, last_year_data, filters)
        if head_row:
            data.append(head_row)
        
        # Add sales persons under this head
        for sp in sp_list:
            # Get customers for this sales person
            customers = get_customers_for_sales_person(sp.name, filters)
            
            if customers:
                for customer in customers:
                    row = create_detail_row(
                        sp, customer, targets, invoices, 
                        last_year_data, filters
                    )
                    if row:
                        data.append(row)
            
            # Add sales person total row
            sp_total = get_sales_person_total(sp, customers, targets, invoices, last_year_data, filters)
            if sp_total:
                sp_total["indent"] = 1
                data.append(sp_total)
    
    # Add grand total
    if data:
        grand_total = get_grand_total(data, filters)
        data.append(grand_total)
    
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
    
    if filters.get("custom_territory"):
        conditions.append("custom_territory = %(custom_territory)s")
        values["custom_territory"] = filters.custom_territory
    
    where_clause = " AND ".join(conditions)
    
    return frappe.db.sql(f"""
        SELECT 
            name,
            sales_person_name,
            parent_sales_person,
            custom_head_sales_code,
            custom_region as region,
            custom_location as location,
            custom_territory as territory,
            custom_sales_person_code as sales_person_code
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
    quarter_fields = get_quarter_fields(filters.month)
    
    targets = frappe.db.sql("""
        SELECT 
            sales_person,
            customer,
            {month_field} as monthly_target,
            {quarter_fields} as quarterly_target,
            (custom_april + custom_may_ + custom_june + custom_july + 
             custom_august + custom_september + custom_october + 
             custom_november + custom_december + custom_january + 
             custom_february + custom_march) as yearly_target
        FROM `tabSales Team`
        WHERE parenttype = 'Customer'
            AND sales_person IN %(sp_names)s
    """.format(
        month_field=month_field,
        quarter_fields=quarter_fields
    ), {
        "sp_names": sp_names
    }, as_dict=True)
    
    # Organize targets by sales person and customer
    target_dict = {}
    for t in targets:
        if t.sales_person not in target_dict:
            target_dict[t.sales_person] = {}
        target_dict[t.sales_person][t.customer] = {
            "monthly": flt(t.monthly_target),
            "quarterly": flt(t.quarterly_target),
            "yearly": flt(t.yearly_target)
        }
    
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


def get_quarter_fields(month):
    """
    Get fields for the quarter containing the given month
    """
    if month in [4, 5, 6]:  # Q1 (Apr-Jun)
        return "(custom_april + custom_may_ + custom_june)"
    elif month in [7, 8, 9]:  # Q2 (Jul-Sep)
        return "(custom_july + custom_august + custom_september)"
    elif month in [10, 11, 12]:  # Q3 (Oct-Dec)
        return "(custom_october + custom_november + custom_december)"
    else:  # Q4 (Jan-Mar)
        return "(custom_january + custom_february + custom_march)"


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
    
    # Join with Sales Team to get sales person
    join_condition = """
        LEFT JOIN `tabSales Team` st 
            ON st.parent = si.name 
            AND st.parenttype = 'Sales Invoice'
    """
    
    where_clause = " AND ".join(conditions)
    
    invoices = frappe.db.sql(f"""
        SELECT 
            si.customer,
            st.sales_person,
            COUNT(DISTINCT si.name) as invoice_count,
            SUM(si.base_net_total) as total_amount,
            SUM(sii.qty) as total_qty,
            AVG(si.base_net_total) as avg_amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        {join_condition}
        WHERE {where_clause}
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
            "amount": flt(inv.total_amount),
            "qty": flt(inv.total_qty),
            "invoice_count": cint(inv.invoice_count),
            "avg_amount": flt(inv.avg_amount)
        }
    
    return invoice_dict


def get_previous_year_data(filters):
    """
    Fetch previous year data for comparison
    """
    if not filters.get("ly_from_date") or not filters.get("ly_to_date"):
        return {}
    
    return frappe.db.sql("""
        SELECT 
            si.customer,
            st.sales_person,
            SUM(si.base_net_total) as amount
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Team` st 
            ON st.parent = si.name 
            AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY si.customer, st.sales_person
    """, {
        "from_date": filters.ly_from_date,
        "to_date": filters.ly_to_date
    }, as_dict=True)


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
            c.customer_name,
            c.customer_group,
            c.territory
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE {where_clause}
        ORDER BY c.customer_name
    """, values, as_dict=True)
    
    return customers


def create_detail_row(sp, customer, targets, invoices, last_year_data, filters):
    """
    Create a detailed row for a sales person-customer combination
    """
    # Get targets
    monthly_target = 0
    quarterly_target = 0
    yearly_target = 0
    
    if filters.include_targets:
        sp_targets = targets.get(sp.name, {})
        customer_targets = sp_targets.get(customer.customer, {})
        monthly_target = customer_targets.get("monthly", 0)
        quarterly_target = customer_targets.get("quarterly", 0)
        yearly_target = customer_targets.get("yearly", 0)
    
    # Get invoice data
    sp_invoices = invoices.get(sp.name, {})
    customer_invoice = sp_invoices.get(customer.customer, {})
    invoice_amount = customer_invoice.get("amount", 0)
    
    # Calculate achievement percentage
    achieved_pct = (invoice_amount / monthly_target * 100) if monthly_target else 0
    
    # Get previous year data
    last_year_amount = 0
    growth_pct = 0
    if filters.get("compare_previous_year"):
        for ly in last_year_data:
            if ly.get("sales_person") == sp.name and ly.get("customer") == customer.customer:
                last_year_amount = flt(ly.get("amount", 0))
                break
        
        if last_year_amount:
            growth_pct = ((invoice_amount - last_year_amount) / last_year_amount * 100)
    
    # Create row
    row = {
        "head_sales_person": sp.parent_sales_person,
        "head_sales_code": sp.custom_head_sales_code,
        "region": sp.region,
        "location": sp.location,
        "territory": sp.territory,
        "sales_person": sp.name,
        "sales_person_code": sp.sales_person_code,
        "customer_name": customer.customer_name,
        "customer_group": customer.customer_group,
        "monthly_target": monthly_target,
        "quarterly_target": quarterly_target,
        "yearly_target": yearly_target,
        "invoice_amount": invoice_amount,
        "achieved_pct": achieved_pct,
        "indent": 2
    }
    
    if filters.get("compare_previous_year"):
        row.update({
            "last_year_amount": last_year_amount,
            "growth_pct": growth_pct
        })
    
    if filters.detailed_view:
        row.update({
            "total_qty": customer_invoice.get("qty", 0),
            "invoice_count": customer_invoice.get("invoice_count", 0),
            "avg_invoice_value": customer_invoice.get("avg_amount", 0)
        })
    
    return row


def get_sales_person_total(sp, customers, targets, invoices, last_year_data, filters):
    """
    Calculate totals for a sales person
    """
    if not customers:
        return None
    
    total_monthly_target = 0
    total_quarterly_target = 0
    total_yearly_target = 0
    total_invoice = 0
    total_last_year = 0
    total_qty = 0
    total_invoice_count = 0
    
    sp_targets = targets.get(sp.name, {})
    sp_invoices = invoices.get(sp.name, {})
    
    for customer in customers:
        # Add targets
        customer_targets = sp_targets.get(customer.customer, {})
        total_monthly_target += customer_targets.get("monthly", 0)
        total_quarterly_target += customer_targets.get("quarterly", 0)
        total_yearly_target += customer_targets.get("yearly", 0)
        
        # Add invoices
        customer_invoice = sp_invoices.get(customer.customer, {})
        total_invoice += customer_invoice.get("amount", 0)
        total_qty += customer_invoice.get("qty", 0)
        total_invoice_count += customer_invoice.get("invoice_count", 0)
        
        # Add previous year
        if filters.get("compare_previous_year"):
            for ly in last_year_data:
                if ly.get("sales_person") == sp.name and ly.get("customer") == customer.customer:
                    total_last_year += flt(ly.get("amount", 0))
                    break
    
    # Calculate percentages
    achieved_pct = (total_invoice / total_monthly_target * 100) if total_monthly_target else 0
    growth_pct = 0
    if total_last_year:
        growth_pct = ((total_invoice - total_last_year) / total_last_year * 100)
    
    # Create total row
    row = {
        "head_sales_person": sp.parent_sales_person,
        "sales_person": sp.name + " - Total",
        "sales_person_code": sp.sales_person_code,
        "customer_name": f"<b>Total for {sp.sales_person_name}</b>",
        "monthly_target": total_monthly_target,
        "quarterly_target": total_quarterly_target,
        "yearly_target": total_yearly_target,
        "invoice_amount": total_invoice,
        "achieved_pct": achieved_pct,
        "is_total_row": 1
    }
    
    if filters.get("compare_previous_year"):
        row.update({
            "last_year_amount": total_last_year,
            "growth_pct": growth_pct
        })
    
    if filters.detailed_view:
        row.update({
            "total_qty": total_qty,
            "invoice_count": total_invoice_count,
            "avg_invoice_value": (total_invoice / total_invoice_count) if total_invoice_count else 0
        })
    
    return row


def get_head_summary(head_name, sp_list, targets, invoices, last_year_data, filters):
    """
    Create summary row for a head sales person
    """
    if head_name == "No Head":
        return None
    
    total_monthly_target = 0
    total_quarterly_target = 0
    total_yearly_target = 0
    total_invoice = 0
    total_last_year = 0
    total_qty = 0
    total_invoice_count = 0
    
    for sp in sp_list:
        # Get customers for this sales person
        customers = get_customers_for_sales_person(sp.name, filters)
        
        sp_targets = targets.get(sp.name, {})
        sp_invoices = invoices.get(sp.name, {})
        
        for customer in customers:
            # Add targets
            customer_targets = sp_targets.get(customer.customer, {})
            total_monthly_target += customer_targets.get("monthly", 0)
            total_quarterly_target += customer_targets.get("quarterly", 0)
            total_yearly_target += customer_targets.get("yearly", 0)
            
            # Add invoices
            customer_invoice = sp_invoices.get(customer.customer, {})
            total_invoice += customer_invoice.get("amount", 0)
            total_qty += customer_invoice.get("qty", 0)
            total_invoice_count += customer_invoice.get("invoice_count", 0)
    
    if total_invoice == 0 and total_monthly_target == 0:
        return None
    
    achieved_pct = (total_invoice / total_monthly_target * 100) if total_monthly_target else 0
    
    row = {
        "head_sales_person": head_name,
        "customer_name": f"<b>HEAD: {head_name}</b>",
        "monthly_target": total_monthly_target,
        "quarterly_target": total_quarterly_target,
        "yearly_target": total_yearly_target,
        "invoice_amount": total_invoice,
        "achieved_pct": achieved_pct,
        "indent": 0,
        "bold": 1
    }
    
    if filters.detailed_view:
        row.update({
            "total_qty": total_qty,
            "invoice_count": total_invoice_count,
            "avg_invoice_value": (total_invoice / total_invoice_count) if total_invoice_count else 0
        })
    
    return row


def get_grand_total(data, filters):
    """
    Calculate grand total for the report
    """
    total_monthly_target = 0
    total_quarterly_target = 0
    total_yearly_target = 0
    total_invoice = 0
    total_last_year = 0
    total_qty = 0
    total_invoice_count = 0
    
    for row in data:
        if row.get("is_total_row") or "HEAD:" in row.get("customer_name", ""):
            continue
            
        total_monthly_target += flt(row.get("monthly_target", 0))
        total_quarterly_target += flt(row.get("quarterly_target", 0))
        total_yearly_target += flt(row.get("yearly_target", 0))
        total_invoice += flt(row.get("invoice_amount", 0))
        total_last_year += flt(row.get("last_year_amount", 0))
        total_qty += flt(row.get("total_qty", 0))
        total_invoice_count += cint(row.get("invoice_count", 0))
    
    achieved_pct = (total_invoice / total_monthly_target * 100) if total_monthly_target else 0
    growth_pct = ((total_invoice - total_last_year) / total_last_year * 100) if total_last_year else 0
    
    grand_total = {
        "customer_name": "<b>GRAND TOTAL</b>",
        "monthly_target": total_monthly_target,
        "quarterly_target": total_quarterly_target,
        "yearly_target": total_yearly_target,
        "invoice_amount": total_invoice,
        "achieved_pct": achieved_pct,
        "is_total_row": 1,
        "bold": 1
    }
    
    if filters.get("compare_previous_year"):
        grand_total.update({
            "last_year_amount": total_last_year,
            "growth_pct": growth_pct
        })
    
    if filters.detailed_view:
        grand_total.update({
            "total_qty": total_qty,
            "invoice_count": total_invoice_count,
            "avg_invoice_value": (total_invoice / total_invoice_count) if total_invoice_count else 0
        })
    
    return grand_total


@frappe.whitelist()
def get_customer_details(customer, sales_person, month, year):
    """
    Get detailed invoice information for a specific customer and sales person
    Used for drill-down functionality
    """
    from_date = get_first_day(f"{year}-{month:02d}-01")
    to_date = get_last_day(f"{year}-{month:02d}-01")
    
    details = frappe.db.sql("""
        SELECT 
            si.name as invoice_no,
            si.posting_date,
            sii.item_name,
            sii.qty,
            sii.base_net_amount as amount
        FROM
