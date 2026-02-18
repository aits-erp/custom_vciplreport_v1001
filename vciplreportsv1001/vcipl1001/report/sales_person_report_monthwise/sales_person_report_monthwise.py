import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months
from calendar import month_name

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    # Get the selected view type
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


# ==================== VIEW 1: CATEGORY WISE (Customer/Head) ====================
def get_category_wise_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Customer", "fieldname": "customer", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "LY Achievement", "fieldname": "ly_ach", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    
    # Get all customers with targets
    customers = get_customers_with_targets(filters)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        
        for cust in customers:
            # Get sales amount for this month
            sales_amount = get_monthly_sales(cust.customer, month, filters)
            
            # Get target for this month
            target = get_monthly_target(cust.customer, month)
            
            # Get last year achievement
            ly_ach = get_ly_achievement(cust.customer, month, filters)
            
            achieved_pct = (sales_amount / target * 100) if target else 0
            
            if sales_amount > 0 or target > 0:
                data.append({
                    "month": month_name,
                    "customer": cust.customer_name,
                    "tso_name": cust.tso_name,
                    "target": target,
                    "ly_ach": ly_ach,
                    "achieved_pct": round(achieved_pct, 2)
                })
        
        # Add month total
        month_total = get_month_total(month, filters)
        if month_total > 0:
            data.append({
                "month": month_name,
                "customer": f"<b>TOTAL - {month_name}</b>",
                "tso_name": "",
                "target": month_total.get("target", 0),
                "ly_ach": month_total.get("ly_ach", 0),
                "achieved_pct": month_total.get("achieved_pct", 0),
                "is_total": 1
            })
    
    # Add YTD Total
    ytd_data = get_ytd_total(filters)
    data.append({
        "month": "<b>TOTAL YTD</b>",
        "customer": "",
        "tso_name": "",
        "target": ytd_data.get("target", 0),
        "ly_ach": ytd_data.get("ly_ach", 0),
        "achieved_pct": ytd_data.get("achieved_pct", 0),
        "is_total": 1
    })
    
    # Add Annual Total
    annual_data = get_annual_total(filters)
    data.append({
        "month": "<b>TOTAL ANNUAL</b>",
        "customer": "",
        "tso_name": "",
        "target": annual_data.get("target", 0),
        "ly_ach": annual_data.get("ly_ach", 0),
        "achieved_pct": annual_data.get("achieved_pct", 0),
        "is_total": 1
    })
    
    return columns, data


# ==================== VIEW 2: DISTRIBUTOR + TSO WISE ====================
def get_distributor_tso_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Distributor", "fieldname": "distributor", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Product Category", "fieldname": "category", "width": 150},
        {"label": "Sales", "fieldname": "sales", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    
    # Get all distributors (customers)
    distributors = get_distributors(filters)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        
        for dist in distributors:
            # Get TSOs for this distributor
            tsos = get_tsos_for_distributor(dist.customer, filters)
            
            for tso in tsos:
                # Get product categories
                categories = get_product_categories()
                
                for cat in categories:
                    sales = get_category_sales(dist.customer, tso.tso, cat, month, filters)
                    target = get_category_target(dist.customer, tso.tso, cat, month)
                    
                    if sales > 0 or target > 0:
                        data.append({
                            "month": month_name,
                            "distributor": dist.customer_name,
                            "tso_name": tso.tso_name,
                            "category": cat,
                            "sales": sales,
                            "target": target,
                            "achieved_pct": round((sales/target*100), 2) if target else 0
                        })
    
    return columns, data


# ==================== VIEW 3: HEAD WISE SUMMARY ====================
def get_head_wise_summary(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Head Name", "fieldname": "head_name", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "LY Achievement", "fieldname": "ly_ach", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    
    # Get all sales heads
    heads = get_sales_heads(filters)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        
        for head in heads:
            # Get TSOs under this head
            tsos = get_tsos_under_head(head.head, filters)
            
            for tso in tsos:
                sales = get_tso_sales(tso.tso, month, filters)
                target = get_tso_target(tso.tso, month)
                ly_ach = get_tso_ly_achievement(tso.tso, month, filters)
                
                if sales > 0 or target > 0:
                    data.append({
                        "month": month_name,
                        "head_name": head.head_name,
                        "tso_name": tso.tso_name,
                        "target": target,
                        "ly_ach": ly_ach,
                        "achieved_pct": round((sales/target*100), 2) if target else 0
                    })
    
    return columns, data


# ==================== VIEW 4: TSO WISE CATEGORY ====================
def get_tso_category_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Distributor", "fieldname": "distributor", "width": 250},
        {"label": "Category", "fieldname": "category", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    data = []
    
    # Get all TSOs
    tsos = get_all_tsos(filters)
    
    for month in range(1, 13):
        month_name = get_month_name(month)
        
        for tso in tsos:
            # Get distributors for this TSO
            distributors = get_distributors_for_tso(tso.tso, filters)
            
            for dist in distributors:
                # Get categories
                categories = get_product_categories()
                
                for cat in categories:
                    sales = get_category_sales_by_tso(tso.tso, dist.distributor, cat, month, filters)
                    target = get_category_target_by_tso(tso.tso, dist.distributor, cat, month)
                    
                    if sales > 0 or target > 0:
                        data.append({
                            "month": month_name,
                            "tso_name": tso.tso_name,
                            "distributor": dist.distributor_name,
                            "category": cat,
                            "target": target,
                            "achieved_pct": round((sales/target*100), 2) if target else 0
                        })
    
    return columns, data


# ==================== HELPER FUNCTIONS ====================

def get_month_name(month):
    months = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]
    return months[month-1] if month <= 12 else ""

def get_customers_with_targets(filters):
    return frappe.db.sql("""
        SELECT DISTINCT c.name as customer, c.customer_name, sp.sales_person_name as tso_name
        FROM `tabCustomer` c
        LEFT JOIN `tabSales Team` st ON st.parent = c.name AND st.parenttype = 'Customer'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE c.disabled = 0
    """, as_dict=True)

def get_monthly_sales(customer, month, filters):
    year = getdate(filters.from_date).year
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    result = frappe.db.sql("""
        SELECT SUM(base_net_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND customer = %s
        AND posting_date BETWEEN %s AND %s
    """, (customer, from_date, to_date), as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_monthly_target(customer, month):
    month_field = get_month_field(month)
    
    result = frappe.db.sql(f"""
        SELECT SUM({month_field}) as total
        FROM `tabSales Team`
        WHERE parenttype = 'Customer' AND parent = %s
    """, customer, as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_ly_achievement(customer, month, filters):
    year = getdate(filters.from_date).year - 1
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    result = frappe.db.sql("""
        SELECT SUM(base_net_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND customer = %s
        AND posting_date BETWEEN %s AND %s
    """, (customer, from_date, to_date), as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_month_total(month, filters):
    year = getdate(filters.from_date).year
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    sales = frappe.db.sql("""
        SELECT SUM(base_net_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND posting_date BETWEEN %s AND %s
    """, (from_date, to_date), as_dict=True)
    
    target = frappe.db.sql("""
        SELECT SUM(custom_january + custom_february + custom_march + 
                   custom_april + custom_may_ + custom_june + custom_july + 
                   custom_august + custom_september + custom_october + 
                   custom_november + custom_december) as total
        FROM `tabSales Team`
        WHERE parenttype = 'Customer'
    """, as_dict=True)
    
    sales_amt = flt(sales[0].total) if sales else 0
    target_amt = flt(target[0].total) if target else 0
    
    return {
        "target": target_amt,
        "ly_ach": 0,
        "achieved_pct": round((sales_amt/target_amt*100), 2) if target_amt else 0
    }

def get_ytd_total(filters):
    # Get YTD (April to current month)
    current_month = getdate(filters.to_date).month
    year = getdate(filters.from_date).year
    
    total_sales = 0
    total_target = 0
    
    for month in range(4, current_month + 1):
        from_date = f"{year}-{month:02d}-01"
        to_date = get_last_day(from_date)
        
        sales = frappe.db.sql("""
            SELECT SUM(base_net_total) as total
            FROM `tabSales Invoice`
            WHERE docstatus = 1
            AND posting_date BETWEEN %s AND %s
        """, (from_date, to_date), as_dict=True)
        
        total_sales += flt(sales[0].total) if sales else 0
    
    return {
        "target": total_target,
        "ly_ach": 0,
        "achieved_pct": 0
    }

def get_annual_total(filters):
    year = getdate(filters.from_date).year
    
    sales = frappe.db.sql("""
        SELECT SUM(base_net_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND YEAR(posting_date) = %s
    """, year, as_dict=True)
    
    return {
        "target": 0,
        "ly_ach": flt(sales[0].total) if sales else 0,
        "achieved_pct": 0
    }

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

def get_distributors(filters):
    return frappe.db.sql("""
        SELECT name as customer, customer_name
        FROM `tabCustomer`
        WHERE customer_group = 'Distributor' OR disabled = 0
    """, as_dict=True)

def get_tsos_for_distributor(distributor, filters):
    return frappe.db.sql("""
        SELECT DISTINCT sp.name as tso, sp.sales_person_name as tso_name
        FROM `tabSales Team` st
        JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE st.parenttype = 'Customer' AND st.parent = %s
    """, distributor, as_dict=True)

def get_product_categories():
    return ["CAST IRON", "PLATINUM", "PC Inner Lid", "PC OUTER LID", "VINOD LEGACY"]

def get_category_sales(distributor, tso, category, month, filters):
    year = getdate(filters.from_date).year
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    result = frappe.db.sql("""
        SELECT SUM(sii.base_net_amount) as total
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
            AND si.customer = %s
            AND (st.sales_person = %s OR %s = '')
            AND i.item_group = %s
            AND si.posting_date BETWEEN %s AND %s
    """, (distributor, tso, tso, category, from_date, to_date), as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_category_target(distributor, tso, category, month):
    month_field = get_month_field(month)
    
    result = frappe.db.sql(f"""
        SELECT {month_field} as target
        FROM `tabSales Team`
        WHERE parenttype = 'Customer' 
            AND parent = %s 
            AND sales_person = %s
    """, (distributor, tso), as_dict=True)
    
    return flt(result[0].target) if result else 0

def get_sales_heads(filters):
    return frappe.db.sql("""
        SELECT DISTINCT parent_sales_person as head, 
               (SELECT sales_person_name FROM `tabSales Person` WHERE name = parent_sales_person) as head_name
        FROM `tabSales Person`
        WHERE parent_sales_person IS NOT NULL
        GROUP BY parent_sales_person
    """, as_dict=True)

def get_tsos_under_head(head, filters):
    return frappe.db.sql("""
        SELECT name as tso, sales_person_name as tso_name
        FROM `tabSales Person`
        WHERE parent_sales_person = %s AND enabled = 1
    """, head, as_dict=True)

def get_tso_sales(tso, month, filters):
    year = getdate(filters.from_date).year
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    result = frappe.db.sql("""
        SELECT SUM(si.base_net_total) as total
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
            AND st.sales_person = %s
            AND si.posting_date BETWEEN %s AND %s
    """, (tso, from_date, to_date), as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_tso_target(tso, month):
    month_field = get_month_field(month)
    
    result = frappe.db.sql(f"""
        SELECT SUM({month_field}) as total
        FROM `tabSales Team`
        WHERE parenttype = 'Customer' AND sales_person = %s
    """, tso, as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_tso_ly_achievement(tso, month, filters):
    year = getdate(filters.from_date).year - 1
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    result = frappe.db.sql("""
        SELECT SUM(si.base_net_total) as total
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
            AND st.sales_person = %s
            AND si.posting_date BETWEEN %s AND %s
    """, (tso, from_date, to_date), as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_all_tsos(filters):
    return frappe.db.sql("""
        SELECT name as tso, sales_person_name as tso_name
        FROM `tabSales Person`
        WHERE enabled = 1
    """, as_dict=True)

def get_distributors_for_tso(tso, filters):
    return frappe.db.sql("""
        SELECT DISTINCT st.parent as distributor, c.customer_name as distributor_name
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE st.parenttype = 'Customer' AND st.sales_person = %s
    """, tso, as_dict=True)

def get_category_sales_by_tso(tso, distributor, category, month, filters):
    year = getdate(filters.from_date).year
    from_date = f"{year}-{month:02d}-01"
    to_date = get_last_day(from_date)
    
    result = frappe.db.sql("""
        SELECT SUM(sii.base_net_amount) as total
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        WHERE si.docstatus = 1
            AND si.customer = %s
            AND i.item_group = %s
            AND si.posting_date BETWEEN %s AND %s
            AND EXISTS (
                SELECT 1 FROM `tabSales Team` st 
                WHERE st.parent = si.name 
                AND st.parenttype = 'Sales Invoice' 
                AND st.sales_person = %s
            )
    """, (distributor, category, from_date, to_date, tso), as_dict=True)
    
    return flt(result[0].total) if result else 0

def get_category_target_by_tso(tso, distributor, category, month):
    month_field = get_month_field(month)
    
    result = frappe.db.sql(f"""
        SELECT {month_field} as target
        FROM `tabSales Team`
        WHERE parenttype = 'Customer' 
            AND parent = %s 
            AND sales_person = %s
    """, (distributor, tso), as_dict=True)
    
    return flt(result[0].target) if result else 0
