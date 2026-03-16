frappe.query_reports["TSO WISE CATEGORYWISE"] = {
    "filters": [
        {
            "fieldname": "parent_sales_person",
            "label": "Sales Head",
            "fieldtype": "Link",
            "options": "Sales Person",
            "reqd": 1
        }
    ]
};