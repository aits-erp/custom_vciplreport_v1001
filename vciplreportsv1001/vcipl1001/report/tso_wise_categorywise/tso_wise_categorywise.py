import frappe
from frappe.utils import flt, getdate, add_months
from frappe import _
import json

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    # Get enhanced data
    categories = get_categories(filters)
    columns = get_enhanced_columns(categories)
    data = get_enhanced_data(filters, categories)
    
    # Add metrics for dashboard
    metrics = get_dashboard_metrics(data, categories)
    
    # Add trends
    trends = get_trend_analysis(data, categories)
    
    # Add heatmap data
    heatmap = get_heatmap_data(data, categories)
    
    return {
        "columns": columns,
        "data": data,
        "chart": get_advanced_chart(data, categories),
        "summary": metrics,
        "trends": trends,
        "heatmap": heatmap
    }

def get_enhanced_columns(categories):
    """Modern columns with better formatting"""
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
            "label": _("💰 Total Sales"),
            "fieldname": "total_achieved",
            "fieldtype": "Currency",
            "width": 150,
            "align": "right"
        },
        {
            "label": _("📈 Performance"),
            "fieldname": "performance_indicator",
            "fieldtype": "Data",
            "width": 120,
            "align": "center"
        },
        {
            "label": _("🎯 Target Achievement"),
            "fieldname": "target_percentage",
            "fieldtype": "Percent",
            "width": 150,
            "align": "center"
        }
    ]
    
    # Add category columns with visual indicators
    for cat in categories[:8]:  # Show top 8 categories
        safe = cat.replace(" ", "_").replace("-", "_")
        columns.append({
            "label": _(f"🏷️ {cat[:15]}"),
            "fieldname": f"{safe}_achieved",
            "fieldtype": "Currency",
            "width": 160,
            "align": "right"
        })
        columns.append({
            "label": _(f"📊 {cat[:10]} Trend"),
            "fieldname": f"{safe}_trend",
            "fieldtype": "Data",
            "width": 100,
            "align": "center"
        })
    
    return columns

def get_enhanced_data(filters, categories):
    """Get data with performance metrics and trends"""
    # Your existing data fetch logic here (from previous code)
    # Add these enhancements:
    
    data = get_base_data(filters, categories)  # Call your existing function
    
    # Enhance data with performance metrics
    for row in data:
        # Add performance indicator
        total = row.get("total_achieved", 0)
        if total > 1000000:
            row["performance_indicator"] = "🚀 Excellent"
            row["performance_class"] = "achievement-high"
        elif total > 500000:
            row["performance_indicator"] = "📈 Good"
            row["performance_class"] = "achievement-medium"
        else:
            row["performance_indicator"] = "⚠️ Needs Improvement"
            row["performance_class"] = "achievement-low"
        
        # Add target achievement (example: assume target is 10% growth)
        row["target_percentage"] = min(flt((total / 100000) * 100), 100)
        
        # Add trend indicators for each category
        for cat in categories:
            safe = cat.replace(" ", "_").replace("-", "_")
            value = row.get(f"{safe}_achieved", 0)
            if value > 100000:
                row[f"{safe}_trend"] = "📈"
            elif value > 0:
                row[f"{safe}_trend"] = "➡️"
            else:
                row[f"{safe}_trend"] = "📉"
    
    return data

def get_dashboard_metrics(data, categories):
    """Create modern dashboard metrics"""
    if not data:
        return []
    
    total_sales = sum(row.get("total_achieved", 0) for row in data)
    avg_monthly = total_sales / len(data) if data else 0
    
    # Calculate growth
    if len(data) > 1:
        current_month = data[-1].get("total_achieved", 0)
        previous_month = data[-2].get("total_achieved", 0)
        growth = ((current_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
    else:
        growth = 0
    
    # Category performance
    category_performance = {}
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        total = sum(row.get(f"{safe}_achieved", 0) for row in data)
        category_performance[cat] = total
    
    top_category = max(category_performance.items(), key=lambda x: x[1]) if category_performance else (None, 0)
    zero_categories = [cat for cat, val in category_performance.items() if val == 0]
    
    metrics = [
        {
            "label": "Total Revenue",
            "value": total_sales,
            "icon": "💰",
            "color": "gradient-purple",
            "indicator": "up" if growth > 0 else "down",
            "percentage": growth
        },
        {
            "label": "Monthly Average",
            "value": avg_monthly,
            "icon": "📊",
            "color": "gradient-blue"
        },
        {
            "label": "Growth Rate",
            "value": f"{growth:.1f}%",
            "icon": "📈",
            "color": "gradient-green",
            "indicator": "up" if growth > 0 else "down"
        },
        {
            "label": "Top Category",
            "value": top_category[0],
            "subvalue": top_category[1],
            "icon": "🏆",
            "color": "gradient-gold"
        },
        {
            "label": "Zero Sales Categories",
            "value": len(zero_categories),
            "icon": "⚠️",
            "color": "gradient-red",
            "tooltip": ", ".join(zero_categories[:5])
        }
    ]
    
    return metrics

def get_trend_analysis(data, categories):
    """Generate trend analysis with sparklines"""
    trends = {
        "monthly_trend": [],
        "category_trends": {},
        "insights": []
    }
    
    # Monthly trend
    months = sorted(set(row.get("month") for row in data))
    for month in months:
        month_data = [row for row in data if row.get("month") == month]
        total = sum(row.get("total_achieved", 0) for row in month_data)
        trends["monthly_trend"].append({"month": month, "value": total})
    
    # Category trends
    for cat in categories[:5]:
        safe = cat.replace(" ", "_").replace("-", "_")
        cat_trend = []
        for month in months:
            month_data = [row for row in data if row.get("month") == month]
            value = sum(row.get(f"{safe}_achieved", 0) for row in month_data)
            cat_trend.append(value)
        trends["category_trends"][cat] = cat_trend
    
    # Generate insights
    if len(trends["monthly_trend"]) >= 2:
        last_month = trends["monthly_trend"][-1]["value"]
        prev_month = trends["monthly_trend"][-2]["value"]
        if last_month > prev_month:
            trends["insights"].append({
                "type": "positive",
                "text": f"📈 Sales increased by {((last_month-prev_month)/prev_month*100):.1f}% compared to previous month"
            })
        else:
            trends["insights"].append({
                "type": "negative", 
                "text": f"📉 Sales decreased by {((prev_month-last_month)/prev_month*100):.1f}% compared to previous month"
            })
    
    # Find best performing region
    regions = {}
    for row in data:
        region = row.get("custom_region")
        if region:
            regions[region] = regions.get(region, 0) + row.get("total_achieved", 0)
    if regions:
        best_region = max(regions, key=regions.get)
        trends["insights"].append({
            "type": "positive",
            "text": f"🏆 Best performing region: {best_region} with {frappe.format(regions[best_region], 'Currency')}"
        })
    
    return trends

def get_heatmap_data(data, categories):
    """Generate data for heatmap visualization"""
    heatmap = {
        "months": sorted(set(row.get("month") for row in data)),
        "regions": list(set(row.get("custom_region") for row in data if row.get("custom_region"))),
        "data": {}
    }
    
    for region in heatmap["regions"]:
        region_data = [row for row in data if row.get("custom_region") == region]
        heatmap["data"][region] = {}
        for month in heatmap["months"]:
            month_data = [row for row in region_data if row.get("month") == month]
            total = sum(row.get("total_achieved", 0) for row in month_data)
            heatmap["data"][region][month] = total
    
    return heatmap

def get_advanced_chart(data, categories):
    """Create advanced interactive chart"""
    if not data:
        return None
    
    # Prepare datasets
    months = sorted(set(row.get("month") for row in data))
    datasets = []
    
    # Add main trend line
    monthly_totals = []
    for month in months:
        month_data = [row for row in data if row.get("month") == month]
        total = sum(row.get("total_achieved", 0) for row in month_data)
        monthly_totals.append(total)
    
    datasets.append({
        "name": "Total Sales",
        "values": monthly_totals,
        "chartType": "line",
        "color": "#667eea"
    })
    
    # Add top 3 categories as bars
    cat_totals = {}
    for cat in categories:
        safe = cat.replace(" ", "_").replace("-", "_")
        cat_total = sum(row.get(f"{safe}_achieved", 0) for row in data)
        cat_totals[cat] = cat_total
    
    top_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for cat, total in top_cats:
        if total > 0:
            cat_data = []
            for month in months:
                month_data = [row for row in data if row.get("month") == month]
                safe = cat.replace(" ", "_").replace("-", "_")
                value = sum(row.get(f"{safe}_achieved", 0) for row in month_data)
                cat_data.append(value)
            
            datasets.append({
                "name": cat,
                "values": cat_data,
                "chartType": "bar",
                "color": "#" + hex(hash(cat) % 0xFFFFFF)[2:].zfill(6)
            })
    
    return {
        "data": {
            "labels": months,
            "datasets": datasets
        },
        "type": "mixed",
        "height": 400,
        "axisOptions": {
            "xAxisMode": "tick",
            "yAxisMode": "tick",
            "xIsSeries": 1
        }
    }