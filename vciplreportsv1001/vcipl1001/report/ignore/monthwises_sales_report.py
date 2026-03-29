# frappe/your_app/your_app/report/comprehensive_sales_report/comprehensive_sales_report.py

import frappe
from frappe.utils import flt, get_first_day, get_last_day, add_years, nowdate
import json


def execute(filters=None):
    filters = frappe._dict(filters or {})
    report_type = filters.get("report_type", "Combined View")
    
    if report_type == "Item Category Wise":
        return execute_item_category_report(filters)
    elif report_type == "Sales Person Wise":
        return execute_sales_person_report(filters)
    else:
        return execute_combined_report(filters)


# --------------------------------------------------
# ITEM CATEGORY REPORT (from your first report)
# --------------------------------------------------
def execute_item_category_report(filters):
    data, customers = get_pivot_data(filters)
    columns = get_item_columns(customers)
    return columns, data


def get_item_columns(customers):
    columns = [
        {"label": "Item Group", "fieldname": "item_group", "width": 180},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 180},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 180}
    ]
    
    for customer in customers:
        columns.append({
            "label": customer,
            "fieldname": frappe.scrub(customer),
            "fieldtype": "Currency",
            "width": 150
        })
    
    columns.append({"fieldname": "popup_data", "hidden": 1})
    return columns


def get_pivot_data(filters):
    conditions = ""
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }
    
    if filters.customer:
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.customer
    
    if filters.item_group:
        conditions += " AND i.item_group = %(item_group)s"
        values["item_group"] = filters.item_group
    
    if filters.custom_main_group:
        conditions += " AND i.custom_main_group = %(custom_main_group)s"
        values["custom_main_group"] = filters.custom_main_group
    
    if filters.custom_sub_group:
        conditions += " AND i.custom_sub_group = %(custom_sub_group)s"
        values["custom_sub_group"] = filters.custom_sub_group
    
    if filters.custom_item_type:
        conditions += " AND i.custom_item_type = %(custom_item_type)s"
        values["custom_item_type"] = filters.custom_item_type
    
    if filters.parent_sales_person:
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.parent_sales_person
    
    raw_data = frappe.db.sql(f"""
        SELECT
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            c.customer_name,
            sii.item_name,
            sii.qty,
            sii.base_net_amount AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
    """, values, as_dict=True)
    
    customers = sorted({row.customer_name for row in raw_data})
    result = {}
    
    for row in raw_data:
        item_group = row.item_group or "Undefined"
        main_group = row.custom_main_group or "Undefined"
        sub_group = row.custom_sub_group or "Undefined"
        customer = row.customer_name
        
        key = f"{item_group}::{main_group}::{sub_group}"
        cust = frappe.scrub(customer)
        
        if key not in result:
            result[key] = {
                "item_group": item_group,
                "custom_main_group": main_group,
                "custom_sub_group": sub_group,
                "popup_data": {}
            }
            for c in customers:
                sc = frappe.scrub(c)
                result[key][sc] = 0
                result[key]["popup_data"][sc] = {}
        
        result[key][cust] += flt(row.amount)
        
        # Aggregate popup data
        items = result[key]["popup_data"][cust]
        if row.item_name not in items:
            items[row.item_name] = {"item_name": row.item_name, "qty": 0, "amount": 0}
        
        items[row.item_name]["qty"] += flt(row.qty)
        items[row.item_name]["amount"] += flt(row.amount)
    
    # Process popup data
    for k in result:
        for cust in result[k]["popup_data"]:
            item_list = list(result[k]["popup_data"][cust].values())
            total_qty = sum(i["qty"] for i in item_list)
            total_amt = sum(i["amount"] for i in item_list)
            
            item_list.append({
                "item_name": "<b>Total</b>",
                "qty": total_qty,
                "amount": total_amt
            })
            
            result[k]["popup_data"][cust] = item_list
        
        result[k]["popup_data"] = json.dumps(result[k]["popup_data"])
    
    return list(result.values()), customers


# --------------------------------------------------
# SALES PERSON REPORT (from your second report)
# --------------------------------------------------
def execute_sales_person_report(filters):
    set_default_filters(filters)
    return get_sales_person_columns(), get_sales_person_data(filters)


def set_default_filters(filters):
    today = nowdate()
    year = int(today[:4])
    month = int(today[5:7])
    
    filters.period_type = filters.get("period_type") or "Month"
    filters.year = int(filters.get("year") or year)
    filters.month = int(filters.get("month") or month)
    filters.quarter = filters.get("quarter") or "Q1"
    filters.half_year = filters.get("half_year") or "H1"


def get_sales_person_columns():
    return [
        {"label": "Head Sales Person", "fieldname": "head_sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Head Sales Code", "fieldname": "custom_head_sales_code", "width": 140},
        {"label": "Region", "fieldname": "region", "width": 120},
        {"label": "Location", "fieldname": "location", "width": 150},
        {"label": "Territory", "fieldname": "territory", "width": 140},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"label": "Customer Name", "fieldname": "customer_name", "width": 220},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 130},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved Target %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 140},
        {"label": "Last Year Achievement", "fieldname": "last_year_amount", "fieldtype": "Currency", "width": 170},
    ]


def get_months(filters):
    if filters.period_type == "Quarter":
        q_map = {
            "Q1": [4, 5, 6],
            "Q2": [7, 8, 9],
            "Q3": [10, 11, 12],
            "Q4": [1, 2, 3],
        }
        return q_map.get(filters.quarter, [4, 5, 6])
    
    if filters.period_type == "Half Year":
        return [4, 5, 6, 7, 8, 9] if filters.half_year == "H1" else [10, 11, 12, 1, 2, 3]
    
    return [int(filters.month)]


def get_date_range(filters):
    months = get_months(filters)
    year = int(filters.year)
    
    from_date = get_first_day(f"{year}-{months[0]}-01")
    to_date = get_last_day(f"{year}-{months[-1]}-01")
    
    return from_date, to_date


def get_sales_person_data(filters):
    from_date, to_date = get_date_range(filters)
    
    ly_from = add_years(from_date, -1)
    ly_to = add_years(to_date, -1)
    
    # Apply filters
    conditions = ""
    values = {}
    
    if filters.get("custom_region"):
        conditions += " AND sp.custom_region = %(custom_region)s"
        values["custom_region"] = filters.custom_region
    
    if filters.get("custom_location"):
        conditions += " AND sp.custom_location = %(custom_location)s"
        values["custom_location"] = filters.custom_location
    
    if filters.get("custom_territory"):
        conditions += " AND sp.custom_territory = %(custom_territory)s"
        values["custom_territory"] = filters.custom_territory
    
    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.parent_sales_person
    
    if filters.get("customer"):
        conditions += " AND c.name = %(customer)s"
        values["customer"] = filters.customer
    
    sales_persons = frappe.db.sql(f"""
        SELECT name, parent_sales_person, custom_head_sales_code,
               custom_region, custom_location, custom_territory
        FROM `tabSales Person`
        WHERE enabled = 1 {conditions.replace('sp.', '')}
    """, values, as_dict=True)
    
    sp_map = {sp.name: sp for sp in sales_persons}
    
    month_fields = {
        1: "custom_january", 2: "custom_february", 3: "custom_march",
        4: "custom_april", 5: "custom_may_", 6: "custom_june",
        7: "custom_july", 8: "custom_august", 9: "custom_september",
        10: "custom_october", 11: "custom_november", 12: "custom_december",
    }
    
    months = get_months(filters)
    target_expr = " + ".join([f"COALESCE(st.{month_fields[m]},0)" for m in months])
    
    # Build customer conditions
    customer_condition = ""
    if filters.get("customer"):
        customer_condition = " AND c.name = %(customer)s"
    
    targets = frappe.db.sql(f"""
        SELECT
            st.sales_person,
            c.name AS customer,
            c.customer_name,
            ({target_expr}) AS target
        FROM `tabSales Team` st
        JOIN `tabCustomer` c ON c.name = st.parent
        WHERE st.parenttype = 'Customer' {customer_condition}
    """, values, as_dict=True)
    
    # Get invoices
    invoices = frappe.db.sql("""
        SELECT customer, SUM(base_net_total) amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY customer
    """, {"f": from_date, "t": to_date}, as_dict=True)
    
    invoice_map = {i.customer: flt(i.amount) for i in invoices}
    
    # Last year invoices
    last_year = frappe.db.sql("""
        SELECT customer, SUM(base_net_total) amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY customer
    """, {"f": ly_from, "t": ly_to}, as_dict=True)
    
    last_year_map = {i.customer: flt(i.amount) for i in last_year}
    
    # Build data
    data = []
    total_target = total_invoice = 0
    
    for t in targets:
        sp = sp_map.get(t.sales_person)
        if not sp:
            continue
        
        parent_sp = sp_map.get(sp.parent_sales_person)
        
        target = flt(t.target)
        invoice = invoice_map.get(t.customer, 0)
        achieved_pct = (invoice / target * 100) if target else 0
        
        total_target += target
        total_invoice += invoice
        
        data.append({
            "head_sales_person": sp.parent_sales_person,
            "custom_head_sales_code": parent_sp.custom_head_sales_code if parent_sp else None,
            "region": sp.custom_region,
            "location": sp.custom_location,
            "territory": sp.custom_territory,
            "sales_person": t.sales_person,
            "customer_name": t.customer_name,
            "target": target,
            "invoice_amount": invoice,
            "achieved_pct": achieved_pct,
            "last_year_amount": last_year_map.get(t.customer, 0),
        })
    
    if data:
        data.append({
            "customer_name": "TOTAL",
            "target": total_target,
            "invoice_amount": total_invoice,
            "achieved_pct": (total_invoice / total_target * 100) if total_target else 0,
        })
    
    return data


# --------------------------------------------------
# COMBINED REPORT VIEW
# --------------------------------------------------
def execute_combined_report(filters):
    """
    Combines both reports into a hierarchical view
    """
    columns = get_combined_columns()
    data = get_combined_data(filters)
    return columns, data


def get_combined_columns():
    return [
        {"label": "Level", "fieldname": "level", "width": 100},
        {"label": "Sales Person / Item Group", "fieldname": "name", "width": 250},
        {"label": "Region/Main Group", "fieldname": "group1", "width": 150},
        {"label": "Location/Sub Group", "fieldname": "group2", "width": 150},
        {"label": "Customer/Item Type", "fieldname": "group3", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 130},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_pct", "fieldtype": "Percent", "width": 120},
        {"label": "Last Year", "fieldname": "last_year", "fieldtype": "Currency", "width": 130},
        {"label": "Growth %", "fieldname": "growth_pct", "fieldtype": "Percent", "width": 120},
    ]


def get_combined_data(filters):
    """
    Creates a hierarchical view combining sales person and item data
    """
    combined_data = []
    
    # Get sales person data
    sales_data = get_sales_person_summary(filters)
    
    # Get item category data
    item_data = get_item_category_summary(filters)
    
    # Add section headers and data
    if sales_data:
        combined_data.append({
            "level": "1",
            "name": "SALES PERSON PERFORMANCE",
            "group1": "",
            "group2": "",
            "group3": "",
            "target": "",
            "invoice_amount": "",
            "achieved_pct": "",
            "last_year": "",
            "growth_pct": "",
            "bold": 1,
            "italic": 0
        })
        combined_data.extend(sales_data)
    
    if item_data:
        combined_data.append({
            "level": "1",
            "name": "ITEM CATEGORY ANALYSIS",
            "group1": "",
            "group2": "",
            "group3": "",
            "target": "",
            "invoice_amount": "",
            "achieved_pct": "",
            "last_year": "",
            "growth_pct": "",
            "bold": 1,
            "italic": 0
        })
        combined_data.extend(item_data)
    
    return combined_data


def get_sales_person_summary(filters):
    """
    Get summarized sales person data
    """
    data = get_sales_person_data(filters)
    summary = []
    
    for row in data:
        if row.get("customer_name") == "TOTAL":
            continue
            
        summary.append({
            "level": "2",
            "name": row.get("customer_name", ""),
            "group1": row.get("region", ""),
            "group2": row.get("location", ""),
            "group3": row.get("territory", ""),
            "target": row.get("target", 0),
            "invoice_amount": row.get("invoice_amount", 0),
            "achieved_pct": row.get("achieved_pct", 0),
            "last_year": row.get("last_year_amount", 0),
            "growth_pct": calculate_growth(row.get("invoice_amount", 0), row.get("last_year_amount", 0)),
        })
    
    return summary


def get_item_category_summary(filters):
    """
    Get summarized item category data
    """
    data, _ = get_pivot_data(filters)
    summary = []
    
    for row in data:
        # Calculate totals across customers
        total_amount = 0
        for key, value in row.items():
            if key not in ["item_group", "custom_main_group", "custom_sub_group", "popup_data"]:
                if isinstance(value, (int, float)):
                    total_amount += value
        
        summary.append({
            "level": "2",
            "name": row.get("item_group", ""),
            "group1": row.get("custom_main_group", ""),
            "group2": row.get("custom_sub_group", ""),
            "group3": "",
            "target": 0,  # Item categories don't have targets
            "invoice_amount": total_amount,
            "achieved_pct": 0,
            "last_year": 0,  # Would need separate query for last year
            "growth_pct": 0,
        })
    
    return summary


def calculate_growth(current, last_year):
    if last_year and last_year > 0:
        return ((current - last_year) / last_year) * 100
    return 0
