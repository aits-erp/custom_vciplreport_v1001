import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day
from calendar import month_name
import json

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    view_type = filters.get("view_type", "CATEGORY WISE (Customer/Head)")
    
    if view_type == "CATEGORY WISE (Customer/Head)":
        return get_category_wise_data(filters)
    elif view_type == "DISTRIBUTOR + TSO WISE":
        return get_distributor_tso_data(filters)
    elif view_type == "HEAD WISE SUMMARY":
        return get_head_wise_summary(filters)
    elif view_type == "TSO WISE CATEGORY":
        return get_tso_category_data(filters)
    else:
        return get_category_wise_data(filters)


# ==================== VIEW 1: CATEGORY WISE ====================
def get_category_wise_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Customer", "fieldname": "customer_name", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Region", "fieldname": "custom_region", "width": 120},
        {"label": "Location", "fieldname": "custom_location", "width": 150},
        {"label": "Territory", "fieldname": "custom_territory_name", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "LY Achievement", "fieldname": "ly_ach", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    year = getdate(filters.from_date).year
    
    # Get all customers with targets
    customers = frappe.db.sql("""
        SELECT DISTINCT 
            c.name as customer,
            c.customer_name,
            sp.name as tso,
            sp.sales_person_name as tso_name,
            sp.custom_region,
            sp.custom_location,
            sp.custom_territory_name
        FROM `tabCustomer` c
        LEFT JOIN `tabSales Team` st ON st.parent = c.name AND st.parenttype = 'Customer'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE c.disabled = 0
    """, as_dict=True)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        from_date = f"{year}-{month:02d}-01"
        to_date = get_last_day(from_date)
        
        for cust in customers:
            if not cust.customer:
                continue
                
            # Get sales amount
            sales = frappe.db.sql("""
                SELECT SUM(base_net_total) as total
                FROM `tabSales Invoice`
                WHERE docstatus = 1 
                    AND customer = %s
                    AND posting_date BETWEEN %s AND %s
            """, (cust.customer, from_date, to_date), as_dict=True)
            sales_amt = flt(sales[0].total) if sales else 0
            
            # Get target
            target_amt = 0
            if cust.tso:
                month_field = get_month_field(month)
                target = frappe.db.sql(f"""
                    SELECT {month_field} as target
                    FROM `tabSales Team`
                    WHERE parenttype = 'Customer' 
                        AND parent = %s
                        AND sales_person = %s
                """, (cust.customer, cust.tso), as_dict=True)
                target_amt = flt(target[0].target) if target else 0
            
            # Get LY achievement
            ly_from = f"{year-1}-{month:02d}-01"
            ly_to = get_last_day(ly_from)
            ly_sales = frappe.db.sql("""
                SELECT SUM(base_net_total) as total
                FROM `tabSales Invoice`
                WHERE docstatus = 1 
                    AND customer = %s
                    AND posting_date BETWEEN %s AND %s
            """, (cust.customer, ly_from, ly_to), as_dict=True)
            ly_amt = flt(ly_sales[0].total) if ly_sales else 0
            
            achieved_pct = (sales_amt / target_amt * 100) if target_amt else 0
            
            if sales_amt > 0 or target_amt > 0:
                data.append({
                    "month": month_name,
                    "customer_name": cust.customer_name,
                    "tso_name": cust.tso_name or "",
                    "custom_region": cust.custom_region or "",
                    "custom_location": cust.custom_location or "",
                    "custom_territory_name": cust.custom_territory_name or "",
                    "target": target_amt,
                    "ly_ach": ly_amt,
                    "achieved_pct": round(achieved_pct, 2)
                })
    
    # Calculate totals - FIXED: Now using numbers, not dictionaries
    total_target = sum(d.get("target", 0) for d in data if isinstance(d.get("target"), (int, float)))
    total_ly = sum(d.get("ly_ach", 0) for d in data if isinstance(d.get("ly_ach"), (int, float)))
    
    # Add YTD totals
    if data:
        data.append({
            "month": "<b>TOTAL YTD</b>",
            "customer_name": "",
            "tso_name": "",
            "custom_region": "",
            "custom_location": "",
            "custom_territory_name": "",
            "target": total_target,
            "ly_ach": total_ly,
            "achieved_pct": 0,
            "is_total": 1
        })
    
    return columns, data


# ==================== VIEW 2: DISTRIBUTOR + TSO WISE ====================
def get_distributor_tso_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Distributor", "fieldname": "distributor", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Item Group", "fieldname": "item_group", "width": 150},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 150},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 150},
        {"label": "Sales", "fieldname": "sales", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    year = getdate(filters.from_date).year
    
    # Get all distributors (customers)
    distributors = frappe.db.sql("""
        SELECT name as customer, customer_name
        FROM `tabCustomer`
        WHERE disabled = 0
    """, as_dict=True)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        from_date = f"{year}-{month:02d}-01"
        to_date = get_last_day(from_date)
        
        for dist in distributors:
            if not dist.customer:
                continue
                
            # Get TSOs for this distributor
            tsos = frappe.db.sql("""
                SELECT DISTINCT 
                    sp.name as tso,
                    sp.sales_person_name as tso_name
                FROM `tabSales Team` st
                JOIN `tabSales Person` sp ON sp.name = st.sales_person
                WHERE st.parenttype = 'Customer' 
                    AND st.parent = %s
            """, dist.customer, as_dict=True)
            
            for tso in tsos:
                if not tso.tso:
                    continue
                    
                # Get item groups from sales
                items = frappe.db.sql("""
                    SELECT 
                        i.item_group,
                        i.custom_main_group,
                        i.custom_sub_group,
                        SUM(sii.base_net_amount) as amount
                    FROM `tabSales Invoice` si
                    JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
                    JOIN `tabItem` i ON i.name = sii.item_code
                    LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
                    WHERE si.docstatus = 1
                        AND si.customer = %s
                        AND st.sales_person = %s
                        AND si.posting_date BETWEEN %s AND %s
                    GROUP BY i.item_group, i.custom_main_group, i.custom_sub_group
                """, (dist.customer, tso.tso, from_date, to_date), as_dict=True)
                
                for item in items:
                    # Get target for this combination
                    month_field = get_month_field(month)
                    target = frappe.db.sql(f"""
                        SELECT {month_field} as target
                        FROM `tabSales Team`
                        WHERE parenttype = 'Customer'
                            AND parent = %s
                            AND sales_person = %s
                    """, (dist.customer, tso.tso), as_dict=True)
                    target_amt = flt(target[0].target) if target else 0
                    
                    data.append({
                        "month": month_name,
                        "distributor": dist.customer_name,
                        "tso_name": tso.tso_name,
                        "item_group": item.item_group or "",
                        "custom_main_group": item.custom_main_group or "",
                        "custom_sub_group": item.custom_sub_group or "",
                        "sales": item.amount,
                        "target": target_amt,
                        "achieved_pct": round((item.amount/target_amt*100), 2) if target_amt else 0
                    })
    
    return columns, data


# ==================== VIEW 3: HEAD WISE SUMMARY ====================
def get_head_wise_summary(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Head Sales Person", "fieldname": "head_sales_person", "width": 200},
        {"label": "Head Code", "fieldname": "custom_head_sales_code", "width": 120},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Region", "fieldname": "custom_region", "width": 120},
        {"label": "Location", "fieldname": "custom_location", "width": 150},
        {"label": "Territory", "fieldname": "custom_territory_name", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    year = getdate(filters.from_date).year
    
    # Get all heads (parent sales persons)
    heads = frappe.db.sql("""
        SELECT DISTINCT 
            parent_sales_person as head,
            (SELECT custom_head_sales_code FROM `tabSales Person` WHERE name = parent_sales_person) as head_code
        FROM `tabSales Person`
        WHERE parent_sales_person IS NOT NULL AND parent_sales_person != ''
    """, as_dict=True)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        from_date = f"{year}-{month:02d}-01"
        to_date = get_last_day(from_date)
        
        for head in heads:
            if not head.head:
                continue
                
            # Get TSOs under this head
            tsos = frappe.db.sql("""
                SELECT 
                    name as tso,
                    sales_person_name as tso_name,
                    custom_region,
                    custom_location,
                    custom_territory_name
                FROM `tabSales Person`
                WHERE parent_sales_person = %s
                    AND enabled = 1
            """, head.head, as_dict=True)
            
            for tso in tsos:
                if not tso.tso:
                    continue
                    
                # Get sales for this TSO
                sales = frappe.db.sql("""
                    SELECT SUM(si.base_net_total) as total
                    FROM `tabSales Invoice` si
                    LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
                    WHERE si.docstatus = 1
                        AND st.sales_person = %s
                        AND si.posting_date BETWEEN %s AND %s
                """, (tso.tso, from_date, to_date), as_dict=True)
                sales_amt = flt(sales[0].total) if sales else 0
                
                # Get target for this TSO
                month_field = get_month_field(month)
                target = frappe.db.sql(f"""
                    SELECT SUM({month_field}) as total
                    FROM `tabSales Team`
                    WHERE parenttype = 'Customer'
                        AND sales_person = %s
                """, tso.tso, as_dict=True)
                target_amt = flt(target[0].total) if target else 0
                
                if sales_amt > 0 or target_amt > 0:
                    data.append({
                        "month": month_name,
                        "head_sales_person": head.head,
                        "custom_head_sales_code": head.head_code or "",
                        "tso_name": tso.tso_name,
                        "custom_region": tso.custom_region or "",
                        "custom_location": tso.custom_location or "",
                        "custom_territory_name": tso.custom_territory_name or "",
                        "target": target_amt,
                        "invoice_amount": sales_amt,
                        "achieved_pct": round((sales_amt/target_amt*100), 2) if target_amt else 0
                    })
    
    return columns, data


# ==================== VIEW 4: TSO WISE CATEGORY ====================
def get_tso_category_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Customer", "fieldname": "customer_name", "width": 250},
        {"label": "Item Group", "fieldname": "item_group", "width": 150},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 150},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 150},
        {"label": "Sales", "fieldname": "sales", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    year = getdate(filters.from_date).year
    
    # Get all TSOs
    tsos = frappe.db.sql("""
        SELECT name as tso, sales_person_name as tso_name
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        from_date = f"{year}-{month:02d}-01"
        to_date = get_last_day(from_date)
        
        for tso in tsos:
            if not tso.tso:
                continue
                
            # Get customers for this TSO
            customers = frappe.db.sql("""
                SELECT DISTINCT 
                    st.parent as customer,
                    c.customer_name
                FROM `tabSales Team` st
                JOIN `tabCustomer` c ON c.name = st.parent
                WHERE st.parenttype = 'Customer'
                    AND st.sales_person = %s
            """, tso.tso, as_dict=True)
            
            for cust in customers:
                if not cust.customer:
                    continue
                    
                # Get sales by item group
                items = frappe.db.sql("""
                    SELECT 
                        i.item_group,
                        i.custom_main_group,
                        i.custom_sub_group,
                        SUM(sii.base_net_amount) as amount
                    FROM `tabSales Invoice` si
                    JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
                    JOIN `tabItem` i ON i.name = sii.item_code
                    LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
                    WHERE si.docstatus = 1
                        AND si.customer = %s
                        AND st.sales_person = %s
                        AND si.posting_date BETWEEN %s AND %s
                    GROUP BY i.item_group, i.custom_main_group, i.custom_sub_group
                """, (cust.customer, tso.tso, from_date, to_date), as_dict=True)
                
                for item in items:
                    # Get target for this combination
                    month_field = get_month_field(month)
                    target = frappe.db.sql(f"""
                        SELECT {month_field} as target
                        FROM `tabSales Team`
                        WHERE parenttype = 'Customer'
                            AND parent = %s
                            AND sales_person = %s
                    """, (cust.customer, tso.tso), as_dict=True)
                    target_amt = flt(target[0].target) if target else 0
                    
                    data.append({
                        "month": month_name,
                        "tso_name": tso.tso_name,
                        "customer_name": cust.customer_name,
                        "item_group": item.item_group or "",
                        "custom_main_group": item.custom_main_group or "",
                        "custom_sub_group": item.custom_sub_group or "",
                        "sales": item.amount,
                        "target": target_amt,
                        "achieved_pct": round((item.amount/target_amt*100), 2) if target_amt else 0
                    })
    
    return columns, data


# ==================== HELPER FUNCTIONS ====================
def get_month_name(month):
    months = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]
    return months[month-1] if 1 <= month <= 12 else ""

def get_month_field(month):
    fields = {
        1: "custom_january", 2: "custom_february", 3: "custom_march",
        4: "custom_april", 5: "custom_may_", 6: "custom_june",
        7: "custom_july", 8: "custom_august", 9: "custom_september",
        10: "custom_october", 11: "custom_november", 12: "custom_december"
    }
    return fields.get(month, "custom_january")

def get_last_day(date):
    from dateutil.relativedelta import relativedelta
    from datetime import datetime
    dt = datetime.strptime(date, "%Y-%m-%d")
    last_day = dt + relativedelta(day=31)
    return last_day.strftime("%Y-%m-%d")
