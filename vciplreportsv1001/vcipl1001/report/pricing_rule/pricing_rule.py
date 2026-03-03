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
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150
        },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",  # Changed from apply_on_item_group
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",  # Changed from apply_on_item_code
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "label": _("Brand"),
            "fieldname": "brand",  # Changed from apply_on_brand
            "fieldtype": "Link",
            "options": "Brand",
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
            "label": _("Discount %"),
            "fieldname": "discount_percentage",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Discount Amount"),
            "fieldname": "discount_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Rate or Discount"),
            "fieldname": "rate_or_discount",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 150
        },
        {
            "label": _("Selling"),
            "fieldname": "selling",
            "fieldtype": "Check",
            "width": 70
        },
        {
            "label": _("Buying"),
            "fieldname": "buying",
            "fieldtype": "Check",
            "width": 70
        },
        {
            "label": _("Priority"),
            "fieldname": "priority",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Disabled"),
            "fieldname": "disable",
            "fieldtype": "Check",
            "width": 70
        },
        {
            "label": _("Price or Product Discount"),
            "fieldname": "price_or_product_discount",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Free Item"),
            "fieldname": "free_item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "label": _("Free Qty"),
            "fieldname": "free_qty",
            "fieldtype": "Float",
            "width": 100
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
            "label": _("Created By"),
            "fieldname": "owner",
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
            "label": _("Modified On"),
            "fieldname": "modified",
            "fieldtype": "Date",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = []
    values = {}
    
    # Period filters (from-to date) based on valid_from and valid_upto
    if filters.get("from_date"):
        conditions.append("(pr.valid_from >= %(from_date)s OR pr.valid_from IS NULL)")
        values["from_date"] = filters["from_date"]
    
    if filters.get("to_date"):
        conditions.append("(pr.valid_upto <= %(to_date)s OR pr.valid_upto IS NULL)")
        values["to_date"] = filters["to_date"]
    
    # Optional: Add active on date filter
    if filters.get("active_on_date"):
        conditions.append("""
            ((pr.valid_from <= %(active_on_date)s OR pr.valid_from IS NULL) 
            AND (pr.valid_upto >= %(active_on_date)s OR pr.valid_upto IS NULL))
        """)
        values["active_on_date"] = filters["active_on_date"]
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Note: The Pricing Rule stores item details in child tables
    # We need to get them from the appropriate child tables based on apply_on
    query = f"""
        SELECT
            pr.name,
            pr.title,
            pr.apply_on,
            pr.customer,
            pr.supplier,
            pr.valid_from,
            pr.valid_upto,
            pr.rate,
            pr.discount_percentage,
            pr.discount_amount,
            pr.rate_or_discount,
            pr.company,
            pr.selling,
            pr.buying,
            pr.priority,
            pr.disable,
            pr.price_or_product_discount,
            pr.free_item,
            pr.free_qty,
            pr.min_qty,
            pr.max_qty,
            pr.owner,
            pr.creation,
            pr.modified,
            -- Get item details from child tables
            (SELECT item_code FROM `tabPricing Rule Item Code` WHERE parent = pr.name LIMIT 1) as item_code,
            (SELECT item_group FROM `tabPricing Rule Item Group` WHERE parent = pr.name LIMIT 1) as item_group,
            (SELECT brand FROM `tabPricing Rule Brand` WHERE parent = pr.name LIMIT 1) as brand
        FROM
            `tabPricing Rule` pr
        WHERE
            {where_clause}
        ORDER BY
            pr.creation DESC,
            pr.valid_from DESC
        LIMIT 1000
    """
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    # Format dates
    for row in data:
        if row.valid_from:
            row.valid_from = frappe.utils.formatdate(row.valid_from)
        if row.valid_upto:
            row.valid_upto = frappe.utils.formatdate(row.valid_upto)
        if row.creation:
            row.creation = frappe.utils.formatdate(row.creation)
        if row.modified:
            row.modified = frappe.utils.formatdate(row.modified)
    
    return data
