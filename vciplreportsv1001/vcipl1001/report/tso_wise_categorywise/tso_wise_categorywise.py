import frappe
from frappe.utils import flt, getdate
from frappe import _

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    # Validate dates
    if filters.get("from_date") and filters.get("to_date"):
        if getdate(filters.from_date) > getdate(filters.to_date):
            frappe.throw(_("From Date must be before To Date"))
    
    categories = get_categories(filters)
    columns = get_columns(categories)
    data = get_data(filters, categories)
    
    # Add chart for better visualization
    chart = get_chart_data(data, categories)
    
    # Add summary section
    summary = get_summary(data, categories)
    
    return columns, data, None, chart, summary

def get_categories(filters):
    """Fetch categories with proper filtering"""
    if filters.get("custom_main_group"):
        if isinstance(filters.custom_main_group, list):
            return filters.custom_main_group
        return [filters.custom_main_group]
    
    # Get categories from items that have sales in the selected period
    conditions = ""
    values = {}
    
    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")
    
    categories = frappe.db.sql("""
        SELECT DISTINCT i.custom_main_group
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE si.docstatus = 1
        AND i.custom_main_group IS NOT NULL
        AND i.custom_main_group != ''
        {conditions}
        ORDER BY i.custom_main_group
    """.format(conditions=conditions), values, as_dict=0)
    
    return [cat[0] for cat in categories if cat[0]]

def get_columns(categories):
    """Enhanced columns with Target columns for each category"""
    columns = [
        {
            "label": _("Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 100,
            "align": "center"
        },
        {
            "label": _("TSO"),
            "fieldname": "tso_name",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Region"),
            "fieldname": "custom_region",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Head Sales Person"),
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": _("Total Achieved"),
            "fieldname": "total_achieved",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        },
        {
            "label": _("Total Target"),
            "fieldname": "total_target",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        }
    ]
    
    # Add category columns with Target and Achieved side by side
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        columns.append({
            "label": _(f"{cat} (Target)"),
            "fieldname": f"{safe}_target",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        })
        columns.append({
            "label": _(f"{cat} (Achieved)"),
            "fieldname": f"{safe}_achieved",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        })
    
    return columns

def get_month_target(sales_person, month_num, year, category):
    """Fetch target for a specific sales person, month and category"""
    if not sales_person or sales_person == "Unassigned":
        return 0
    
    # Map month number to custom field name
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
    
    month_field = month_fields.get(month_num)
    if not month_field:
        return 0
    
    # Query target from Sales Person child table for specific category
    target = frappe.db.sql("""
        SELECT {month_field}
        FROM `tabSales Person`
        WHERE name = %s
    """.format(month_field=month_field), (sales_person,))
    
    if target and target[0][0]:
        # If target is stored as JSON or has category-wise targets
        # Adjust this based on your actual data structure
        target_value = target[0][0]
        
        # If target is stored as a string like "Nonstick:1000,Hard Anodised:2000"
        if isinstance(target_value, str) and ':' in target_value:
            target_dict = {}
            for item in target_value.split(','):
                if ':' in item:
                    cat, val = item.split(':')
                    target_dict[cat.strip()] = flt(val)
            return target_dict.get(category, 0)
        
        # If target is a single number for all categories
        return flt(target_value)
    
    return 0

def get_data(filters, categories):
    """Improved data fetching with Customer Name, TSO and Target columns"""
    conditions = []
    values = {}
    
    # Get month number from filters
    month_num = None
    if filters.get("from_date"):
        month_num = getdate(filters.from_date).month
    
    # Build conditions
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
        if isinstance(region_list, list):
            placeholders = ','.join(['%s'] * len(region_list))
            conditions.append(f"sp.custom_region IN ({placeholders})")
            values.update({f"region_{i}": reg for i, reg in enumerate(region_list)})
        else:
            conditions.append("sp.custom_region = %(custom_region)s")
            values["custom_region"] = region_list
    
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.get("customer")
    
    if filters.get("customer_group"):
        conditions.append("si.customer_group = %(customer_group)s")
        values["customer_group"] = filters.get("customer_group")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Main query with proper joins including Customer Name
    query = f"""
        SELECT
            DATE_FORMAT(si.posting_date, '%%Y-%%m') as month_key,
            MONTH(si.posting_date) as month_num,
            YEAR(si.posting_date) as year,
            sp.name as tso_name,
            sp.parent_sales_person,
            sp.custom_region,
            c.customer_name as customer_name,
            i.custom_main_group as category,
            SUM(sii.base_net_amount) as achieved,
            COUNT(DISTINCT si.name) as invoice_count,
            COUNT(DISTINCT sii.item_code) as item_count
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        INNER JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        INNER JOIN `tabSales Person` sp ON sp.name = st.sales_person
        INNER JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.docstatus = 1
            AND i.custom_main_group IS NOT NULL
            AND i.custom_main_group != ''
            AND {where_clause}
        GROUP BY 
            DATE_FORMAT(si.posting_date, '%%Y-%%m'),
            MONTH(si.posting_date),
            YEAR(si.posting_date),
            sp.name,
            sp.parent_sales_person,
            sp.custom_region,
            c.customer_name,
            i.custom_main_group
        ORDER BY 
            year ASC,
            month_num ASC,
            sp.name ASC,
            c.customer_name ASC
    """
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    # Process and structure data
    result = {}
    
    for row in data:
        # Create a unique key for each month + TSO + Customer + Head + Region
        key = (row.month_key, row.tso_name, row.customer_name, row.parent_sales_person, row.custom_region)
        
        if key not in result:
            result[key] = {
                "month": f"{MONTHS[int(row.month_num)-1]}-{row.year}",
                "month_num": row.month_num,
                "year": row.year,
                "tso_name": row.tso_name or "Unassigned",
                "customer_name": row.customer_name or "No Customer",
                "parent_sales_person": row.parent_sales_person or "Unassigned",
                "custom_region": row.custom_region or "No Region",
                "total_achieved": 0,
                "total_target": 0,
                "invoice_count": 0,
                "item_count": 0
            }
            
            # Initialize all categories with 0 for target and achieved
            for cat in categories:
                safe = cat.replace(" ", "_").replace("-", "_")
                result[key][f"{safe}_target"] = 0
                result[key][f"{safe}_achieved"] = 0
            
            # Fetch and set targets for each category for this TSO and month
            for cat in categories:
                safe = cat.replace(" ", "_").replace("-", "_")
                target_value = get_month_target(row.tso_name, row.month_num, row.year, cat)
                result[key][f"{safe}_target"] = target_value
                result[key]["total_target"] += target_value
        
        # Add achieved amount for the category
        if row.category in categories:
            safe = row.category.replace(" ", "_").replace("-", "_")
            result[key][f"{safe}_achieved"] += flt(row.achieved)
            result[key]["total_achieved"] += flt(row.achieved)
            result[key]["invoice_count"] += row.invoice_count
            result[key]["item_count"] += row.item_count
    
    # Convert to list and sort
    result_list = list(result.values())
    result_list.sort(key=lambda x: (x["year"], x["month_num"], x["tso_name"], x["customer_name"]))
    
    return result_list

def get_summary(data, categories):
    """Generate summary statistics with category-wise totals"""
    if not data:
        return []
    
    total_sales = sum(row.get("total_achieved", 0) for row in data)
    total_targets = sum(row.get("total_target", 0) for row in data)
    total_invoices = sum(row.get("invoice_count", 0) for row in data)
    
    # Calculate category-wise totals for achieved and target
    category_achieved_totals = {}
    category_target_totals = {}
    
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        category_achieved_totals[cat] = sum(row.get(f"{safe}_achieved", 0) for row in data)
        category_target_totals[cat] = sum(row.get(f"{safe}_target", 0) for row in data)
    
    # Get top performing category by achieved
    top_category = max(category_achieved_totals.items(), key=lambda x: x[1]) if category_achieved_totals else (None, 0)
    
    summary = [
        {
            "value": total_sales,
            "label": _("Total Sales Achieved"),
            "indicator": "Green" if total_sales > 0 else "Red",
            "datatype": "Currency"
        },
        {
            "value": total_targets,
            "label": _("Total Targets"),
            "indicator": "Blue",
            "datatype": "Currency"
        },
        {
            "value": total_invoices,
            "label": _("Total Invoices"),
            "indicator": "Blue",
            "datatype": "Int"
        },
        {
            "value": len(data),
            "label": _("Total Records"),
            "indicator": "Blue",
            "datatype": "Int"
        }
    ]
    
    if top_category[0]:
        summary.append({
            "value": top_category[1],
            "label": _("Top Category: {0} (Achieved)").format(top_category[0]),
            "indicator": "Green",
            "datatype": "Currency"
        })
    
    # Add category-wise summary
    for cat in categories[:5]:  # Show top 5 categories in summary
        safe = cat.replace(" ", "_").replace("-", "_")
        achieved_total = category_achieved_totals.get(cat, 0)
        target_total = category_target_totals.get(cat, 0)
        if achieved_total > 0 or target_total > 0:
            summary.append({
                "value": achieved_total,
                "label": _("{0} Achieved").format(cat),
                "indicator": "Green" if achieved_total >= target_total else "Orange",
                "datatype": "Currency"
            })
    
    return summary

def get_chart_data(data, categories):
    """Generate chart data for visualization"""
    if not data:
        return None
    
    # Prepare data for chart - show achieved vs target for top categories
    months = sorted(set([row["month"] for row in data]))
    chart_data = {
        "data": {
            "labels": months,
            "datasets": []
        },
        "type": "bar",
        "height": 300,
        "colors": ["#28a745", "#007bff", "#dc3545", "#ffc107", "#17a2b8", "#6c757d"]
    }
    
    # Add datasets for top 3 categories only (achieved vs target)
    for cat in categories[:3]:  # Limit to top 3 categories
        safe = cat.replace(" ", "_").replace("-", "_")
        
        # Achieved values
        achieved_values = []
        target_values = []
        
        for month in months:
            month_data = [row for row in data if row["month"] == month]
            achieved_total = sum(row.get(f"{safe}_achieved", 0) for row in month_data)
            target_total = sum(row.get(f"{safe}_target", 0) for row in month_data)
            achieved_values.append(achieved_total)
            target_values.append(target_total)
        
        if sum(achieved_values) > 0 or sum(target_values) > 0:
            chart_data["data"]["datasets"].append({
                "name": f"{cat} (Achieved)",
                "values": achieved_values,
                "chart_type": "bar"
            })
            chart_data["data"]["datasets"].append({
                "name": f"{cat} (Target)",
                "values": target_values,
                "chart_type": "line"
            })
    
    return chart_data if chart_data["data"]["datasets"] else None