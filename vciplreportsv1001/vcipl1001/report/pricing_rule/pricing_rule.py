# Copyright (c) 2026, Your Organization and contributors
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
            "label": _("Customer Name"),
            "fieldname": "customer_name",
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
            "label": _("Discount %"),
            "fieldname": "discount_percentage",
            "fieldtype": "Percent",
            "width": 100
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
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = []
    values = {}
    
    # Customer filter
    if filters.get("customer"):
        conditions.append("pr.customer = %(customer)s")
        values["customer"] = filters["customer"]
    
    # Customer Name filter
    if filters.get("customer_name"):
        conditions.append("EXISTS (SELECT 1 FROM `tabCustomer` c WHERE c.name = pr.customer AND c.customer_name LIKE %(customer_name)s)")
        values["customer_name"] = f"%{filters['customer_name']}%"
    
    # Date filters
    if filters.get("from_date"):
        conditions.append("(pr.valid_from >= %(from_date)s OR pr.valid_from IS NULL)")
        values["from_date"] = filters["from_date"]
    
    if filters.get("to_date"):
        conditions.append("(pr.valid_upto <= %(to_date)s OR pr.valid_upto IS NULL)")
        values["to_date"] = filters["to_date"]
    
    # Valid on date
    if filters.get("valid_on_date"):
        conditions.append("""
            ((pr.valid_from <= %(valid_on_date)s OR pr.valid_from IS NULL) 
            AND (pr.valid_upto >= %(valid_on_date)s OR pr.valid_upto IS NULL))
        """)
        values["valid_on_date"] = filters["valid_on_date"]
    
    # Company filter
    if filters.get("company"):
        conditions.append("pr.company = %(company)s")
        values["company"] = filters["company"]
    
    # Item Group filter
    if filters.get("item_group"):
        conditions.append("pr.item_group = %(item_group)s")
        values["item_group"] = filters["item_group"]
    
    # Selling/Buying filters
    if filters.get("selling"):
        conditions.append("pr.selling = 1")
    
    if filters.get("buying"):
        conditions.append("pr.buying = 1")
    
    # Active/Disabled filter
    if filters.get("show_disabled") and filters.get("show_disabled") == 1:
        # Show all
        pass
    else:
        conditions.append("(pr.disable = 0 OR pr.disable IS NULL)")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT
            pr.name,
            pr.title,
            pr.apply_on,
            pr.customer,
            (SELECT customer_name FROM `tabCustomer` WHERE name = pr.customer) as customer_name,
            pr.item_group,
            pr.valid_from,
            pr.valid_upto,
            pr.rate,
            pr.discount_percentage,
            pr.company,
            pr.selling,
            pr.buying,
            CASE 
                WHEN pr.disable = 1 THEN 'Disabled'
                WHEN pr.valid_upto IS NOT NULL AND pr.valid_upto < CURDATE() THEN 'Expired'
                WHEN pr.valid_from IS NOT NULL AND pr.valid_from > CURDATE() THEN 'Future'
                ELSE 'Active'
            END as status
        FROM
            `tabPricing Rule` pr
        WHERE
            {where_clause}
        ORDER BY
            pr.modified DESC
        LIMIT 1000
    """
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    # Format dates
    for row in data:
        if row.valid_from:
            row.valid_from = frappe.utils.formatdate(row.valid_from)
        if row.valid_upto:
            row.valid_upto = frappe.utils.formatdate(row.valid_upto)
    
    return data
