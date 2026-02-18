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
                SELECT {month_field} as target
                FROM `tabSales Team`
                WHERE parenttype = 'Customer' AND parent = %s AND sales_person = %s
            """, (row.customer_name, row.tso_name), as_dict=True)
            target = flt(target_data[0].target) if target_data else 0
        
        achieved_pct = (row.sales / target * 100) if target else 0
        
        if filters.show_zero_rows or row.sales > 0 or target > 0:
            data.append({
                "month": month_name,
                "head_sales_person": row.head_sales_person or "",
                "custom_head_sales_code": row.custom_head_sales_code or "",
                "tso_name": row.tso_name or "",
                "customer_name": row.customer_name,
                "custom_region": row.custom_region or "",
                "custom_location": row.custom_location or "",
                "custom_territory_name": row.custom_territory_name or "",
                "sales": row.sales,
                "target": target,
                "achieved_pct": round(achieved_pct, 2)
            })
    
    return columns, data


# ==================== VIEW 4: TSO WISE CATEGORY ====================
def get_tso_category_data(filters):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "TSO Name", "fieldname": "tso_name", "width": 180},
        {"label": "Customer", "fieldname": "customer_name", "width": 250},
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
            sp.sales_person_name as tso_name,
            c.customer_name,
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
        GROUP BY MONTH(si.posting_date), sp.sales_person_name, c.customer_name,
                 sp.parent_sales_person, i.item_group, i.custom_main_group, i.custom_sub_group
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
                SELECT {month_field} as target
                FROM `tabSales Team`
                WHERE parenttype = 'Customer' AND parent = %s AND sales_person = %s
            """, (row.customer_name, row.tso_name), as_dict=True)
            target = flt(target_data[0].target) if target_data else 0
        
        achieved_pct = (row.sales / target * 100) if target else 0
        
        if filters.show_zero_rows or row.sales > 0 or target > 0:
            data.append({
                "month": month_name,
                "tso_name": row.tso_name or "",
                "customer_name": row.customer_name,
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


# ==================== HELPER FUNCTIONS ====================

def get_common_conditions(filters):
    conditions = []
    
    if filters.get("month"):
        conditions.append("MONTH(si.posting_date) = %(month)s")
    
    if filters.get("custom_region"):
        conditions.append("sp.custom_region = %(custom_region)s")
    
    if filters.get("custom_location"):
        conditions.append("sp.custom_location = %(custom_location)s")
    
    if filters.get("custom_territory_name"):
        conditions.append("sp.custom_territory_name = %(custom_territory_name)s")
    
    if filters.get("parent_sales_person"):
        conditions.append("sp.parent_sales_person = %(parent_sales_person)s")
    
    if filters.get("sales_person"):
        conditions.append("sp.name = %(sales_person)s")
    
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
    
    if filters.get("customer_group"):
        conditions.append("c.customer_group = %(customer_group)s")
    
    if filters.get("item_group"):
        conditions.append("i.item_group = %(item_group)s")
    
    if filters.get("custom_main_group"):
        conditions.append("i.custom_main_group = %(custom_main_group)s")
    
    if filters.get("custom_sub_group"):
        conditions.append("i.custom_sub_group = %(custom_sub_group)s")
    
    if filters.get("custom_item_type"):
        conditions.append("i.custom_item_type = %(custom_item_type)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""

def get_filter_values(filters):
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }
    
    if filters.get("month"):
        values["month"] = filters.month
    if filters.get("custom_region"):
        values["custom_region"] = filters.custom_region
    if filters.get("custom_location"):
        values["custom_location"] = filters.custom_location
    if filters.get("custom_territory_name"):
        values["custom_territory_name"] = filters.custom_territory_name
    if filters.get("parent_sales_person"):
        values["parent_sales_person"] = filters.parent_sales_person
    if filters.get("sales_person"):
        values["sales_person"] = filters.sales_person
    if filters.get("customer"):
        values["customer"] = filters.customer
    if filters.get("customer_group"):
        values["customer_group"] = filters.customer_group
    if filters.get("item_group"):
        values["item_group"] = filters.item_group
    if filters.get("custom_main_group"):
        values["custom_main_group"] = filters.custom_main_group
    if filters.get("custom_sub_group"):
        values["custom_sub_group"] = filters.custom_sub_group
    if filters.get("custom_item_type"):
        values["custom_item_type"] = filters.custom_item_type
    
    return values

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
