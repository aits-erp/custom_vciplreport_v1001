import frappe
from frappe.utils import flt, getdate
from frappe import _

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

# Month field mapping for target amounts
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
    """Enhanced columns with better formatting including Customer and Target columns"""
    columns = [
        {
            "label": _("Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 100,
            "align": "center"
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
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
        {
            "label": _("Total Target"),
            "fieldname": "total_target",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        },
        {
            "label": _("Total Achieved"),
            "fieldname": "total_achieved",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        }
    ]
    
    # Add category columns with Target and Achieved
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        columns.append({
            "label": _(f"{cat} (Target)"),
            "fieldname": f"{safe}_target",
            "fieldtype": "Currency",
            "width": 180,
            "align": "right"
        })
        columns.append({
            "label": _(f"{cat} (Achieved)"),
            "fieldname": f"{safe}_achieved",
            "fieldtype": "Currency",
            "width": 180,
            "align": "right"
        })
    
    return columns

def get_data(filters, categories):
    """Improved data fetching with customer and target columns"""
    conditions = []
    values = {}
    
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
    
    # Main query with proper joins including customer
    query = f"""
        SELECT
            DATE_FORMAT(si.posting_date, '%%Y-%%m') as month_key,
            MONTH(si.posting_date) as month_num,
            YEAR(si.posting_date) as year,
            sp.parent_sales_person,
            sp.custom_region,
            si.customer,
            i.custom_main_group as category,
            SUM(sii.base_net_amount) as achieved,
            COUNT(DISTINCT si.name) as invoice_count,
            COUNT(DISTINCT sii.item_code) as item_count
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
            si.customer,
            i.custom_main_group
        ORDER BY 
            year ASC,
            month_num ASC,
            sp.custom_region ASC,
            sp.parent_sales_person ASC,
            si.customer ASC
    """
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    # Get target data for each Sales Person and month
    targets = get_targets(filters, categories)
    
    # Process and structure data
    result = {}
    
    for row in data:
        # Create a unique key for each month + head + region + customer
        key = (row.month_key, row.parent_sales_person, row.custom_region, row.customer)
        
        if key not in result:
            month_num = int(row.month_num)
            year = row.year
            
            # Get targets for this sales person and month
            target_key = (row.parent_sales_person, row.month_key)
            sales_targets = targets.get(target_key, {})
            
            result[key] = {
                "month": f"{MONTHS[month_num-1]}-{year}",
                "month_num": month_num,
                "year": year,
                "parent_sales_person": row.parent_sales_person or "Unassigned",
                "custom_region": row.custom_region or "No Region",
                "customer": row.customer or "No Customer",
                "total_target": 0,
                "total_achieved": 0,
                "invoice_count": 0,
                "item_count": 0
            }
            
            # Initialize all categories with 0 for target and achieved
            for cat in categories:
                safe = cat.replace(" ", "_").replace("-", "_")
                result[key][f"{safe}_target"] = sales_targets.get(cat, 0)
                result[key][f"{safe}_achieved"] = 0
                result[key]["total_target"] += sales_targets.get(cat, 0)
        
        # Add achieved amount for the category
        if row.category in categories:
            safe = row.category.replace(" ", "_").replace("-", "_")
            result[key][f"{safe}_achieved"] += flt(row.achieved)
            result[key]["total_achieved"] += flt(row.achieved)
            result[key]["invoice_count"] += row.invoice_count
            result[key]["item_count"] += row.item_count
    
    # Convert to list and sort
    result_list = list(result.values())
    result_list.sort(key=lambda x: (x["year"], x["month_num"], x["custom_region"], x["customer"]))
    
    return result_list

def get_targets(filters, categories):
    """Fetch targets from Sales Person table based on month fields"""
    targets = {}
    
    # Get date range for filtering
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    
    if not from_date or not to_date:
        return targets
    
    # Build conditions for sales persons
    conditions = []
    values = {}
    
    if filters.get("parent_sales_person"):
        conditions.append("name = %(parent_sales_person)s")
        values["parent_sales_person"] = filters.get("parent_sales_person")
    
    if filters.get("sales_person"):
        conditions.append("name = %(sales_person)s")
        values["sales_person"] = filters.get("sales_person")
    
    if filters.get("custom_region"):
        region_list = filters.get("custom_region")
        if isinstance(region_list, list):
            placeholders = ','.join(['%s'] * len(region_list))
            conditions.append(f"custom_region IN ({placeholders})")
            values.update({f"region_{i}": reg for i, reg in enumerate(region_list)})
        else:
            conditions.append("custom_region = %(custom_region)s")
            values["custom_region"] = region_list
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Fetch all sales persons with their monthly target fields
    sales_persons = frappe.db.sql(f"""
        SELECT name, {', '.join([f'COALESCE({field}, 0) as {field}' for field in month_fields.values()])}
        FROM `tabSales Person`
        WHERE {where_clause}
    """, values, as_dict=1)
    
    # For each month in range, get targets
    current_date = getdate(from_date)
    while current_date <= getdate(to_date):
        month_num = current_date.month
        month_key = f"{current_date.year}-{str(month_num).zfill(2)}"
        month_field = month_fields.get(month_num)
        
        if month_field:
            for sp in sales_persons:
                target_value = flt(sp.get(month_field, 0))
                
                # If categories exist, distribute target across categories
                # Note: Modify this logic based on how category-wise targets are stored
                if categories and target_value > 0:
                    per_category_target = target_value / len(categories)
                    key = (sp.name, month_key)
                    if key not in targets:
                        targets[key] = {}
                    for cat in categories:
                        targets[key][cat] = per_category_target
                else:
                    key = (sp.name, month_key)
                    if key not in targets:
                        targets[key] = {}
                    for cat in categories:
                        targets[key][cat] = 0
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return targets

def get_summary(data, categories):
    """Generate summary statistics"""
    if not data:
        return []
    
    total_sales = sum(row.get("total_achieved", 0) for row in data)
    total_target = sum(row.get("total_target", 0) for row in data)
    total_invoices = sum(row.get("invoice_count", 0) for row in data)
    
    # Calculate category-wise totals
    category_totals = {}
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        category_totals[cat] = sum(row.get(f"{safe}_achieved", 0) for row in data)
    
    # Get top performing category
    top_category = max(category_totals.items(), key=lambda x: x[1]) if category_totals else (None, 0)
    
    summary = [
        {
            "value": total_sales,
            "label": _("Total Sales"),
            "indicator": "Green" if total_sales > 0 else "Red",
            "datatype": "Currency"
        },
        {
            "value": total_target,
            "label": _("Total Target"),
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
        },
        {
            "value": len(set([row.get("customer") for row in data if row.get("customer") != "No Customer"])),
            "label": _("Unique Customers"),
            "indicator": "Blue",
            "datatype": "Int"
        }
    ]
    
    if top_category[0]:
        summary.append({
            "value": top_category[1],
            "label": _("Top Category: {0}").format(top_category[0]),
            "indicator": "Green",
            "datatype": "Currency"
        })
    
    return summary

def get_chart_data(data, categories):
    """Generate chart data for visualization"""
    if not data:
        return None
    
    # Prepare data for chart
    months = sorted(set([row["month"] for row in data]))
    chart_data = {
        "data": {
            "labels": months,
            "datasets": []
        },
        "type": "bar",
        "height": 300,
        "colors": ["#28a745", "#dc3545", "#ffc107", "#17a2b8", "#6c757d", "#007bff"]
    }
    
    # Add datasets for top 5 categories only (to keep chart readable)
    for cat in categories[:5]:  # Limit to top 5 categories
        safe = cat.replace(" ", "_").replace("-", "_")
        values = []
        for month in months:
            month_data = [row for row in data if row["month"] == month]
            total = sum(row.get(f"{safe}_achieved", 0) for row in month_data)
            values.append(total)
        
        if sum(values) > 0:  # Only add if there's data
            chart_data["data"]["datasets"].append({
                "name": cat,
                "values": values
            })
    
    return chart_data if chart_data["data"]["datasets"] else None