frappe.query_reports["CATEGORYWISE"] = {
    "filters": [
        {
            "fieldname": "year",
            "label": "Year",
            "fieldtype": "Int",
            "default": new Date().getFullYear(),
            "reqd": 1
        },
        {
            "fieldname": "main_group",
            "label": "Main Group",
            "fieldtype": "Data"
        },
        {
            "fieldname": "head_sales_person",
            "label": "Head Sales Person",
            "fieldtype": "Link",
            "options": "Sales Person"
        },
        {
            "fieldname": "tso",
            "label": "TSO",
            "fieldtype": "Data"
        },
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer"
        }
    ]
};