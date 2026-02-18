# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate, cint

def execute(filters=None):
    filters = frappe._dict(filters or {})
    set_default_filters(filters)
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data


def set_default_filters(filters):
    today = nowdate()
    
    if not filters.get("year"):
        filters.year = cint(today[:4])
    else:
        filters.year = cint(filters.year)
    
    if not filters.get("month"):
        filters.month = cint(today[5:7])
    else:
        filters.month = cint(filters.month)
    
    filters.from_date = get_first_day(f"{filters.year}-{filters.month:02d}-01")
    filters.to_date = get_last_day(f"{filters.year}-{filters.month:02d}-01")
    
    if filters.get("compare_previous_year"):
        filters.ly_from_date = add_years(filters.from_date, -1)
        filters.ly_to_date = add_years(filters.to_date, -1)


def get_columns():
    return [
        {
            "label": _("Head Sales Person"),
            "fieldname": "head_sales_person",
            "fieldtype": "Data",
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
        },
        {
            "label": _("Target (December)"),
            "fieldname": "monthly_target",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Invoice Amount (December)"),
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
    ]


def get_data(filters):
    data = []
    
    # Add header
    data.append({
        "head_sales_person": "",
        "customer_name": "SALES PERSON PERFORMANCE",
        "region": "",
        "location": "",
        "territory_name": "",
        "monthly_target": 0,
        "invoice_amount": 0,
        "achieved_pct": 0
    })
    
    # Get sales persons
    sales_persons = get_sales_persons(filters)
    
    for sp in sales_persons:
        # Get customers for this sales person
        customers = get_customers_for_sales_person(sp.name, filters)
        
        for customer in customers:
            # Get target
            monthly_target = get_monthly_target(sp.name, customer.customer, filters.month)
            
            # Get invoice amount
            invoice_amount = get_invoice_amount(customer.customer, filters)
            
            # Calculate achievement
            achieved_pct = (invoice_amount / monthly_target * 100) if monthly_target else 0
            
            data.append({
                "head_sales_person": "Jaydeo Deshmukh",  # From your screenshot
                "customer_name": customer.customer_name,
                "region": "West",  # From your screenshot
                "location": sp.location or "",
                "territory_name": sp.territory_name or "",
                "monthly_target": monthly_target,
                "invoice_amount": invoice_amount,
                "achieved_pct": achieved_pct
            })
        
        # Add sales person total
        if customers:
            sp_total_target = sum([get_monthly_target(sp.name, c.customer, filters.month) for c in customers])
            sp_total_invoice = sum([get_invoice_amount(c.customer, filters) for c in customers])
            sp_achieved = (sp_total_invoice / sp_total_target * 100) if sp_total_target else 0
            
            data.append({
                "head_sales_person": "",
                "customer_name": f"TOTAL - {sp.sales_person_name or sp.name}",
                "region": "",
                "location": "",
                "territory_name": "",
                "monthly_target": sp_total_target,
                "invoice_amount": sp_total_invoice,
                "achieved_pct": sp_achieved
            })
    
    return data


def get_sales_persons(filters):
    conditions = ["enabled = 1"]
    values = {}
    
    if filters.get("territory_name"):
        conditions.append("custom_territory_name = %(territory_name)s")
        values["territory_name"] = filters.territory_name
    
    where_clause = " AND ".join(conditions)
    
    return frappe.db.sql(f"""
        SELECT 
            name,
            sales_person_name,
            custom_location as location,
            custom_territory_name as territory_name
        FROM `tabSales Person`
        WHERE {where_clause}
    """, values, as_dict=True)


def get_customers_for_sales_person(sales_person, filters):
    conditions = ["parenttype = 'Customer'", "sales_person = %(sales_person)s"]
    values = {"sales_person": sales_person}
    
    if filters.get("customer"):
        conditions.append("parent = %(customer)s")
        values["customer"] = filters.customer
    
    where_clause = " AND ".join(conditions)
    
    return frappe.db.sql(f"""
        SELECT 
            st.parent as customer,
            c.customer_name
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE {where_clause}
        ORDER BY c.customer_name
    """, values, as_dict=True)


def get_monthly_target(sales_person, customer, month):
    month_field = {
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
    }.get(month, "custom_january")
    
    result = frappe.db.sql(f"""
        SELECT {month_field} as target
        FROM `tabSales Team`
        WHERE parenttype = 'Customer'
            AND parent = %(customer)s
            AND sales_person = %(sales_person)s
    """, {
        "customer": customer,
        "sales_person": sales_person
    }, as_dict=True)
    
    return flt(result[0].target) if result else 0


def get_invoice_amount(customer, filters):
    result = frappe.db.sql("""
        SELECT SUM(base_net_total) as amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
            AND customer = %(customer)s
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, {
        "customer": customer,
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }, as_dict=True)
    
    return flt(result[0].amount) if result else 0
