# Copyright (c) 2024, Your Organization and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {
            "label": _("ID"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Pricing Rule",
            "width": 150
        },
        {
            "label": _("Title"),
            "fieldname": "title",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Apply On"),
            "fieldname": "apply_on",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": _("Custom Customer Name"),
            "fieldname": "custom_customer_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150
        },
        {
            "label": _("Valid From"),
            "fieldname": "valid_from",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Valid Upto"),
            "fieldname": "valid_upto",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Discount Percentage"),
            "fieldname": "discount_percentage",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Min Qty"),
            "fieldname": "min_qty",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": _("Max Qty"),
            "fieldname": "max_qty",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": _("Valid For"),
            "fieldname": "valid_for",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 150
        },
        {
            "label": _("Currency"),
            "fieldname": "currency",
            "fieldtype": "Link",
            "options": "Currency",
            "width": 100
        },
        {
            "label": _("Created By"),
            "fieldname": "created_by",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Modified By"),
            "fieldname": "modified_by",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Created On"),
            "fieldname": "creation",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Tags"),
            "fieldname": "_user_tags",
            "fieldtype": "Data",
            "width": 150
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get pricing rules with customer information
    query = """
        SELECT 
            pr.name,
            pr.title,
            pr.apply_on,
            pr.customer,
            cust.custom_customer_name,
            pr.item_group,
            pr.valid_from,
            pr.valid_upto,
            pr.rate,
            pr.discount_percentage,
            pr.min_qty,
            pr.max_qty,
            CONCAT(IFNULL(pr.valid_from, ''), ' to ', IFNULL(pr.valid_upto, '')) as valid_for,
            pr.company,
            pr.currency,
            pr.owner as created_by,
            pr.modified_by,
            pr.creation,
            pr._user_tags,
            pr.price_or_discount as price_discount_type,
            pr.warehouse,
            pr.brand,
            pr.customer_group,
            pr.territory,
            pr.selling,
            pr.buying,
            pr.applicable_for,
            pr.free_item,
            pr.free_qty,
            pr.threshold_percentage,
            pr.priority,
            pr.coupon_code,
            pr.condition,
            pr.is_cumulative,
            pr.disable,
            pr.mixed_conditions,
            pr.is_conditional,
            pr.same_item,
            pr.rule_description
        FROM 
            `tabPricing Rule` pr
        LEFT JOIN 
            `tabCustomer` cust ON pr.customer = cust.name
        WHERE 
            1=1 {conditions}
        ORDER BY 
            pr.creation DESC, pr.valid_from DESC
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filters, as_dict=1)
    
    # Format the data
    for row in data:
        # Format valid_for string
        if row.valid_from and row.valid_upto:
            row.valid_for = f"{row.valid_from} to {row.valid_upto}"
        elif row.valid_from:
            row.valid_for = f"From {row.valid_from}"
        elif row.valid_upto:
            row.valid_for = f"Until {row.valid_upto}"
        else:
            row.valid_for = "Always Valid"
        
        # Get user full names
        if row.created_by:
            user = frappe.db.get_value("User", row.created_by, "full_name")
            row.created_by = user or row.created_by
        
        if row.modified_by:
            user = frappe.db.get_value("User", row.modified_by, "full_name")
            row.modified_by = user or row.modified_by
    
    return data

def get_conditions(filters):
    conditions = ""
    
    # Customer filter
    if filters.get("customer"):
        conditions += " AND pr.customer = %(customer)s"
    
    # Custom customer name filter (searches in Customer doctype)
    if filters.get("custom_customer_name"):
        conditions += """ AND EXISTS (
            SELECT 1 FROM `tabCustomer` c 
            WHERE c.name = pr.customer 
            AND c.custom_customer_name LIKE %(custom_customer_name)s
        )"""
    
    # Date filters
    if filters.get("from_date"):
        conditions += " AND (pr.valid_from >= %(from_date)s OR pr.valid_from IS NULL OR pr.valid_from = '')"
    
    if filters.get("to_date"):
        conditions += " AND (pr.valid_upto <= %(to_date)s OR pr.valid_upto IS NULL OR pr.valid_upto = '')"
    
    # Active period filter (rules valid during a specific date)
    if filters.get("valid_on_date"):
        conditions += """ AND (
            (pr.valid_from <= %(valid_on_date)s AND pr.valid_upto >= %(valid_on_date)s)
            OR (pr.valid_from <= %(valid_on_date)s AND pr.valid_upto IS NULL)
            OR (pr.valid_from IS NULL AND pr.valid_upto >= %(valid_on_date)s)
            OR (pr.valid_from IS NULL AND pr.valid_upto IS NULL)
        )"""
    
    # Additional filters
    if filters.get("item_group"):
        conditions += " AND pr.item_group = %(item_group)s"
    
    if filters.get("apply_on"):
        conditions += " AND pr.apply_on = %(apply_on)s"
    
    if filters.get("company"):
        conditions += " AND pr.company = %(company)s"
    
    if filters.get("selling") and filters.get("selling") == 1:
        conditions += " AND pr.selling = 1"
    
    if filters.get("buying") and filters.get("buying") == 1:
        conditions += " AND pr.buying = 1"
    
    if filters.get("disable") is not None:
        conditions += " AND pr.disable = %(disable)s"
    
    if filters.get("has_coupon"):
        conditions += " AND pr.coupon_code IS NOT NULL AND pr.coupon_code != ''"
    
    if filters.get("priority"):
        conditions += " AND pr.priority = %(priority)s"
    
    # Tags filter
    if filters.get("tags"):
        conditions += " AND pr._user_tags LIKE %(tags)s"
    
    # Search by ID or Title
    if filters.get("search_text"):
        conditions += """ AND (
            pr.name LIKE %(search_text)s 
            OR pr.title LIKE %(search_text)s
            OR pr.rule_description LIKE %(search_text)s
        )"""
    
    return conditions
