import frappe
from frappe.utils import flt, getdate
from frappe import _
from datetime import datetime

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    # Get categories
    categories = get_categories(filters)
    
    # Get columns with target columns
    columns = get_columns_with_targets(categories)
    
    # Get data with targets
    data = get_data_with_targets(filters, categories)
    
    # Get summary metrics
    summary = get_summary_with_targets(data, categories)
    
    # Get chart data
    chart = get_chart_with_targets(data, categories)
    
    return columns, data, None, chart, summary

def get_categories(filters):
    """Fetch categories from filters or database"""
    if filters.get("custom_main_group"):
        if isinstance(filters.custom_main_group, list):
            return filters.custom_main_group
        return [filters.custom_main_group]
    
    categories = frappe.db.sql("""
        SELECT DISTINCT custom_main_group
        FROM `tabItem`
        WHERE custom_main_group IS NOT NULL
        AND custom_main_group != ''
        ORDER BY custom_main_group
    """, as_dict=0)
    
    return [cat[0] for cat in categories if cat[0]]

def get_columns_with_targets(categories):
    """Create columns with Target columns next to each Category"""
    columns = [
        {
            "label": _("📅 Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 120,
            "align": "center"
        },
        {
            "label": _("📍 Region"),
            "fieldname": "custom_region",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("👤 Head Sales Person"),
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": _("💰 Total Achieved"),
            "fieldname": "total_achieved",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        },
        {
            "label": _("🎯 Total Target"),
            "fieldname": "total_target",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        },
        {
            "label": _("📈 Achievement %"),
            "fieldname": "achievement_percentage",
            "fieldtype": "Percent",
            "width": 120,
            "align": "center"
        }
    ]
    
    # Add category columns with target columns side by side
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        
        # Achieved column
        columns.append({
            "label": _(f"🏷️ {cat[:20]} (Achieved)"),
            "fieldname": f"{safe}_achieved",
            "fieldtype": "Currency",
            "width": 160,
            "align": "right"
        })
        
        # Target column right next to it
        columns.append({
            "label": _(f"🎯 {cat[:20]} (Target)"),
            "fieldname": f"{safe}_target",
            "fieldtype": "Currency",
            "width": 160,
            "align": "right"
        })
    
    return columns

def get_data_with_targets(filters, categories):
    """Get sales data with monthly targets from Sales Person table"""
    
    # Build conditions
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    
    if filters.get("parent_sales_person"):
        conditions.append("sp.parent_sales_person = %(parent_sales_person)s")
        values["parent_sales_person"] = filters.get("parent_sales_person")
    
    if filters.get("sales_person"):
        conditions.append("sp.name = %(sales_person)s")
        values["sales_person"] = filters.get("sales_person")
    
    if filters.get("custom_region"):
        region_list = filters.get("custom_region")
        if isinstance(region_list, list) and region_list:
            placeholders = ','.join(['%s'] * len(region_list))
            conditions.append(f"sp.custom_region IN ({placeholders})")
            for i, reg in enumerate(region_list):
                values[f"region_{i}"] = reg
        elif region_list:
            conditions.append("sp.custom_region = %(custom_region)s")
            values["custom_region"] = region_list
    
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.get("customer")
    
    if filters.get("customer_group"):
        conditions.append("si.customer_group = %(customer_group)s")
        values["customer_group"] = filters.get("customer_group")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get sales data
    sales_query = f"""
        SELECT
            DATE_FORMAT(si.posting_date, '%%Y-%%m') as month_key,
            MONTH(si.posting_date) as month_num,
            YEAR(si.posting_date) as year,
            sp.parent_sales_person,
            sp.custom_region,
            sp.name as sales_person_name,
            i.custom_main_group as category,
            SUM(sii.base_net_amount) as achieved
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        INNER JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        INNER JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
            AND i.custom_main_group IS NOT NULL
            AND i.custom_main_group != ''
            AND {where_clause}
        GROUP BY 
            DATE_FORMAT(si.posting_date, '%%Y-%%m'),
            MONTH(si.posting_date),
            YEAR(si.posting_date),
            sp.parent_sales_person,
            sp.custom_region,
            sp.name,
            i.custom_main_group
    """
    
    sales_data = frappe.db.sql(sales_query, values, as_dict=1)
    
    # Get target data from Sales Person table
    target_query = """
        SELECT
            sp.parent_sales_person,
            sp.custom_region,
            sp.name as sales_person_name,
            CASE 
                WHEN %(month)s = 1 THEN sp.custom_january
                WHEN %(month)s = 2 THEN sp.custom_february
                WHEN %(month)s = 3 THEN sp.custom_march
                WHEN %(month)s = 4 THEN sp.custom_april
                WHEN %(month)s = 5 THEN sp.custom_may_
                WHEN %(month)s = 6 THEN sp.custom_june
                WHEN %(month)s = 7 THEN sp.custom_july
                WHEN %(month)s = 8 THEN sp.custom_august
                WHEN %(month)s = 9 THEN sp.custom_september
                WHEN %(month)s = 10 THEN sp.custom_october
                WHEN %(month)s = 11 THEN sp.custom_november
                WHEN %(month)s = 12 THEN sp.custom_december
            END as monthly_target
        FROM `tabSales Person` sp
        WHERE sp.parent_sales_person IS NOT NULL
    """
    
    # Organize data by month, head, region
    result = {}
    
    for row in sales_data:
        key = (row.month_key, row.parent_sales_person, row.custom_region)
        
        if key not in result:
            result[key] = {
                "month": f"{MONTHS[int(row.month_num)-1]}-{row.year}",
                "month_num": row.month_num,
                "year": row.year,
                "parent_sales_person": row.parent_sales_person or "Unassigned",
                "custom_region": row.custom_region or "No Region",
                "total_achieved": 0,
                "total_target": 0
            }
            
            # Initialize all categories with 0
            for cat in categories:
                safe = cat.replace(" ", "_").replace("-", "_")
                result[key][f"{safe}_achieved"] = 0
                result[key][f"{safe}_target"] = 0
        
        # Add achieved amount
        if row.category in categories:
            safe = row.category.replace(" ", "_").replace("-", "_")
            result[key][f"{safe}_achieved"] += flt(row.achieved)
            result[key]["total_achieved"] += flt(row.achieved)
    
    # Now fetch targets for each combination
    for key in result:
        month_num = result[key]["month_num"]
        
        # Get targets for this month and head
        target_values = {"month": month_num}
        
        targets = frappe.db.sql("""
            SELECT 
                sp.name as sales_person_name,
                CASE 
                    WHEN %(month)s = 1 THEN sp.custom_january
                    WHEN %(month)s = 2 THEN sp.custom_february
                    WHEN %(month)s = 3 THEN sp.custom_march
                    WHEN %(month)s = 4 THEN sp.custom_april
                    WHEN %(month)s = 5 THEN sp.custom_may_
                    WHEN %(month)s = 6 THEN sp.custom_june
                    WHEN %(month)s = 7 THEN sp.custom_july
                    WHEN %(month)s = 8 THEN sp.custom_august
                    WHEN %(month)s = 9 THEN sp.custom_september
                    WHEN %(month)s = 10 THEN sp.custom_october
                    WHEN %(month)s = 11 THEN sp.custom_november
                    WHEN %(month)s = 12 THEN sp.custom_december
                END as monthly_target
            FROM `tabSales Person` sp
            WHERE sp.parent_sales_person = %(parent_sales_person)s
        """, {
            "month": month_num,
            "parent_sales_person": result[key]["parent_sales_person"]
        }, as_dict=1)
        
        # Sum targets for all TSOs under this head
        total_target = 0
        for target_row in targets:
            total_target += flt(target_row.get("monthly_target", 0))
        
        result[key]["total_target"] = total_target
        
        # Distribute target across categories (proportionally based on historical or equally)
        # For now, we'll distribute equally or you can customize this logic
        if categories and total_target > 0:
            target_per_category = total_target / len(categories)
            for cat in categories:
                safe = cat.replace(" ", "_").replace("-", "_")
                result[key][f"{safe}_target"] = target_per_category
        
        # Calculate achievement percentage
        if result[key]["total_target"] > 0:
            result[key]["achievement_percentage"] = (result[key]["total_achieved"] / result[key]["total_target"]) * 100
        else:
            result[key]["achievement_percentage"] = 0
    
    # Convert to list and sort
    result_list = list(result.values())
    result_list.sort(key=lambda x: (x["year"], x["month_num"], x["custom_region"]))
    
    return result_list

def get_summary_with_targets(data, categories):
    """Generate summary with target achievements"""
    if not data:
        return []
    
    total_achieved = sum(row.get("total_achieved", 0) for row in data)
    total_target = sum(row.get("total_target", 0) for row in data)
    overall_achievement = (total_achieved / total_target * 100) if total_target > 0 else 0
    
    # Category-wise achievement
    category_achieved = {}
    category_target = {}
    
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        category_achieved[cat] = sum(row.get(f"{safe}_achieved", 0) for row in data)
        category_target[cat] = sum(row.get(f"{safe}_target", 0) for row in data)
    
    # Find best and worst performing categories
    best_category = None
    best_percentage = 0
    worst_category = None
    worst_percentage = 100
    
    for cat in categories:
        if category_target[cat] > 0:
            percentage = (category_achieved[cat] / category_target[cat]) * 100
            if percentage > best_percentage:
                best_percentage = percentage
                best_category = cat
            if percentage < worst_percentage:
                worst_percentage = percentage
                worst_category = cat
    
    summary = [
        {
            "label": "Total Achieved",
            "value": total_achieved,
            "indicator": "Green",
            "datatype": "Currency",
            "icon": "💰"
        },
        {
            "label": "Total Target",
            "value": total_target,
            "indicator": "Blue",
            "datatype": "Currency",
            "icon": "🎯"
        },
        {
            "label": "Overall Achievement",
            "value": f"{overall_achievement:.1f}%",
            "indicator": "Green" if overall_achievement >= 100 else "Orange",
            "datatype": "Percent",
            "icon": "📈"
        },
        {
            "label": f"Best Category: {best_category}" if best_category else "Best Category",
            "value": f"{best_percentage:.1f}%",
            "indicator": "Green",
            "datatype": "Percent",
            "icon": "🏆"
        },
        {
            "label": f"Needs Improvement: {worst_category}" if worst_category else "Needs Improvement",
            "value": f"{worst_percentage:.1f}%",
            "indicator": "Red",
            "datatype": "Percent",
            "icon": "⚠️"
        }
    ]
    
    return summary

def get_chart_with_targets(data, categories):
    """Generate chart comparing achieved vs target"""
    if not data:
        return None
    
    months = sorted(set(row.get("month") for row in data))
    
    achieved_values = []
    target_values = []
    
    for month in months:
        month_data = [row for row in data if row.get("month") == month]
        achieved = sum(row.get("total_achieved", 0) for row in month_data)
        target = sum(row.get("total_target", 0) for row in month_data)
        achieved_values.append(achieved)
        target_values.append(target)
    
    chart = {
        "data": {
            "labels": months,
            "datasets": [
                {
                    "name": "Achieved",
                    "values": achieved_values,
                    "chartType": "bar",
                    "color": "#28a745"
                },
                {
                    "name": "Target",
                    "values": target_values,
                    "chartType": "line",
                    "color": "#ffc107"
                }
            ]
        },
        "type": "mixed",
        "height": 350,
        "axisOptions": {
            "xAxisMode": "tick",
            "yAxisMode": "tick",
            "xIsSeries": 1
        }
    }
    
    return chart