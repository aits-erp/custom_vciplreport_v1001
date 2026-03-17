frappe.query_reports["CATEGORYWISE"] = {

    "filters": [

        // ✅ Date Range (Mandatory)
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.month_end()
        },

        // ✅ TSO (Sales Person)
        {
            "fieldname": "tso",
            "label": "TSO",
            "fieldtype": "Link",
            "options": "Sales Person",   // 👈 change if different
            "get_query": function () {
                return {
                    filters: {
                        "is_group": 0
                    }
                }
            }
        },

        // ✅ Customer (Distributor)
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer"
        },

        // ✅ Category (Item Group)
        {
            "fieldname": "item_group",
            "label": "Category",
            "fieldtype": "Link",
            "options": "Item Group"
        },

        // ✅ Main Group (Your Custom Field)
        {
            "fieldname": "main_group",
            "label": "Main Group",
            "fieldtype": "Data"
        },

        // ✅ Item
        {
            "fieldname": "item",
            "label": "Item",
            "fieldtype": "Link",
            "options": "Item"
        },

        // ✅ Warehouse (Optional but useful)
        {
            "fieldname": "warehouse",
            "label": "Warehouse",
            "fieldtype": "Link",
            "options": "Warehouse"
        },

        // ✅ Company
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        }

    ]
};