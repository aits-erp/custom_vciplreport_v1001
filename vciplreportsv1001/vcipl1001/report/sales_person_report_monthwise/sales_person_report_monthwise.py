import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day
import json

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    view_type = filters.get("view_type", "TSO WISE CATEGORY")
    
    if view_type == "CATEGORY WISE (Customer/Head)":
        return get_category_wise_data(filters)
    elif view_type == "DISTRIBUTOR + TSO WISE":
        return get_distributor_tso_data(filters)
    elif view_type == "HEAD WISE SUMMARY":
        return get_head_wise_summary(filters)
    elif view_type == "TSO WISE CATEGORY":
        return get_tso_category_data(filters)
    else:
        return get_tso_category_data(filters)


# ==================== VIEW 1: CATEGORY WISE ====================
def get_category_wise_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Customer", "fieldname": "customer_name", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Head Sales Person", "fieldname": "head_sales_person", "width": 180},
        {"label": "Region", "fieldname": "custom_region", "width": 120},
        {"label": "Location", "fieldname": "custom_location", "width": 150},
        {"label": "Territory", "fieldname": "custom_territory_name", "width": 140},
        {"label": "Item Group", "fieldname": "item_group", "width": 150},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 150},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 150},
        {"label": "Sales", "fieldname": "sales", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "LY Achievement", "fieldname": "ly_ach", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    conditions = get_common_conditions(filters)
    data = []
    year = getdate(filters.from_date).year
    
    # Build SQL query based on filters
    sql = """
        SELECT 
            MONTH(si.posting_date) as month_num,
            c.customer_name,
            sp.sales_person_name as tso_name,
            sp.parent_sales_person as head_sales_person,
            sp.custom_region,
            sp.custom_location,
            sp.custom_territory_name,
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            SUM(sii.base_net_amount) as sales
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        GROUP BY MONTH(si.posting_date), c.customer_name, sp.sales_person_name,
                 sp.parent_sales_person, sp.custom_region, sp.custom_location,
                 sp.custom_territory_name, i.item_group, i.custom_main_group, i.custom_sub_group
    """.format(conditions=conditions)
    
    values = get_filter_values(filters)
    results = frappe.db.sql(sql, values, as_dict=True)
    
    months = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]
    
    for row in results:
        month_name = months[row.month_num-1] if row.month_num <= 12 else ""
        
        # Get target
        target = 0
        if filters.include_targets and row.tso_name:
            month_field = get_month_field(row.month_num)
            target_data = frappe.db.sql(f"""
                SELECT {month_field} as target
                FROM `tabSales Team`
                WHERE parenttype = 'Customer' AND parent = %s AND sales_person = %s
            """, (row.customer_name, row.tso_name), as_dict=True)
            target = flt(target_data[0].target) if target_data else 0
        
        # Get LY achievement
        ly_ach = 0
        if filters.compare_previous_year:
            ly_from = f"{year-1}-{row.month_num:02d}-01"
            ly_to = get_last_day(ly_from)
            ly_data = frappe.db.sql("""
                SELECT SUM(base_net_total) as total
                FROM `tabSales Invoice`
                WHERE docstatus = 1 AND customer = %s
                    AND posting_date BETWEEN %s AND %s
            """, (row.customer_name, ly_from, ly_to), as_dict=True)
            ly_ach = flt(ly_data[0].total) if ly_data else 0
        
        achieved_pct = (row.sales / target * 100) if target else 0
        
        if filters.show_zero_rows or row.sales > 0 or target > 0:
            data.append({
                "month": month_name,
                "customer_name": row.customer_name,
                "tso_name": row.tso_name or "",
                "head_sales_person": row.head_sales_person or "",
                "custom_region": row.custom_region or "",
                "custom_location": row.custom_location or "",
                "custom_territory_name": row.custom_territory_name or "",
                "item_group": row.item_group or "",
                "custom_main_group": row.custom_main_group or "",
                "custom_sub_group": row.custom_sub_group or "",
                "sales": row.sales,
                "target": target,
                "ly_ach": ly_ach,
                "achieved_pct": round(achieved_pct, 2)
            })
    
    return columns, data


# ==================== VIEW 2: DISTRIBUTOR + TSO WISE ====================
def get_distributor_tso_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Distributor", "fieldname": "distributor", "width": 250},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Head Sales Person", "fieldname": "head_sales_person", "width": 180},
        {"label": "Region", "fieldname": "custom_region", "width": 120},
        {"label": "Location", "fieldname": "custom_location", "width": 150},
        {"label": "Territory", "fieldname": "custom_territory_name", "width": 140},
        {"label": "Item Group", "fieldname": "item_group", "width": 150},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 150},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 150},
        {"label": "Sales", "fieldname": "sales", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    conditions = get_common_conditions(filters)
    data = []
    
    sql = """
        SELECT 
            MONTH(si.posting_date) as month_num,
            c.customer_name as distributor,
            sp.sales_person_name as tso_name,
            sp.parent_sales_person as head_sales_person,
            sp.custom_region,
            sp.custom_location,
            sp.custom_territory_name,
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            SUM(sii.base_net_amount) as sales
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        GROUP BY MONTH(si.posting_date), c.customer_name, sp.sales_person_name,
                 sp.parent_sales_person, i.item_group, i.custom_main_group, i.custom_sub_group
    """.format(conditions=conditions)
    
    values = get_filter_values(filters)
    results = frappe.db.sql(sql, values, as_dict=True)
    
    months = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]
    
    for row in results:
        month_name = months[row.month_num-1] if row.month_num <= 12 else ""
        
        # Get target
        target = 0
        if filters.include_targets and row.tso_name:
            month_field = get_month_field(row.month_num)
            target_data = frappe.db.sql(f"""
                SELECT {month_field} as target
                FROM `tabSales Team`
                WHERE parenttype = 'Customer' AND parent = %s AND sales_person = %s
            """, (row.distributor, row.tso_name), as_dict=True)
            target = flt(target_data[0].target) if target_data else 0
        
        achieved_pct = (row.sales / target * 100) if target else 0
        
        if filters.show_zero_rows or row.sales > 0 or target > 0:
            data.append({
                "month": month_name,
                "distributor": row.distributor,
                "tso_name": row.tso_name or "",
                "head_sales_person": row.head_sales_person or "",
                "custom_region": row.custom_region or "",
                "custom_location": row.custom_location or "",
                "custom_territory_name": row.custom_territory_name or "",
                "item_group": row.item_group or "",
                "custom_main_group": row.custom_main_group or "",
                "custom_sub_group": row.custom_sub_group or "",
                "sales": row.sales,
                "target": target,
                "achieved_pct": round(achieved_pct, 2)
            })
    
    return columns, data


# ==================== VIEW 3: HEAD WISE SUMMARY ====================
def get_head_wise_summary(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Head Sales Person", "fieldname": "head_sales_person", "width": 200},
        {"label": "Head Code", "fieldname": "custom_head_sales_code", "width": 120},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Customer", "fieldname": "customer_name", "width": 250},
        {"label": "Region", "fieldname": "custom_region", "width": 120},
        {"label": "Location", "fieldname": "custom_location", "width": 150},
        {"label": "Territory", "fieldname": "custom_territory_name", "width": 140},
        {"label": "Sales", "fieldname": "sales", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120}
    ]
    
    conditions = get_common_conditions(filters)
    data = []
    
    sql = """
        SELECT 
            MONTH(si.posting_date) as month_num,
            sp.parent_sales_person as head_sales_person,
            (SELECT custom_head_sales_code FROM `tabSales Person` WHERE name = sp.parent_sales_person) as custom_head_sales_code,
            sp.sales_person_name as tso_name,
            c.customer_name,
            sp.custom_region,
            sp.custom_location,
            sp.custom_territory_name,
            SUM(si.base_net_total) as sales
        FROM `tabSales Invoice` si
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        GROUP BY MONTH(si.posting_date), sp.parent_sales_person, sp.sales_person_name,
                 c.customer_name, sp.custom_region, sp.custom_location, sp.custom_territory_name
    """.format(conditions=conditions)
    
    values = get_filter_values(filters)
    results = frappe.db.sql(sql, values, as_dict=True)
    
    months = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]
    
    for row in results:
        month_name = months[row.month_num-1] if row.month_num <= 12 else ""
        
        # Get target
        target = 0
        if filters.include_targets and row.tso_name and row.customer_name:
            month_field = get_month_field(row.month_num)
            target_data = frappe.db.sql(f"""
                SELECT {
