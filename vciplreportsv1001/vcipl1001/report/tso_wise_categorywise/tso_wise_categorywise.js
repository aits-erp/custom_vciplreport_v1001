frappe.query_reports["TSO WISE CATEGORYWISE"] = {

    onload: function(report) {

        report.set_filter_value("custom_main_group", [
            "Hard Anodised",
            "Nonstick",
            "Horeca",
            "Pressure Cookers",
            "SS Cookware",
            "Healux",
            "Kraft",
            "Platinum",
            "Platinum Triply P.cooker",
            "Cast Iron",
            "Kraft Pressure Cooker",
            "Csd",
            "Cookers Spare Parts",
            "Other Spare"
        ]);
    },

    filters: [

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 1
        },

        {
            fieldname: "sales_person",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ✅ HEAD SALES PERSON (MULTI - NAME)
        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT name
                    FROM \`tabSales Person\`
                    WHERE parent_sales_person IS NULL
                    AND name LIKE %s
                `, ["%" + txt + "%"]);
            }
        },

        // 🔥 REGION
        {
            fieldname: "custom_region",
            label: "Region",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_region
                    FROM \`tabSales Person\`
                    WHERE custom_region IS NOT NULL
                    AND custom_region != ''
                    AND custom_region LIKE %s
                `, ["%" + txt + "%"]);
            }
        },

        // 🔥 HEAD SALES CODE
        {
            fieldname: "custom_head_sales_code",
            label: "Head Sales Code",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_head_sales_code
                    FROM \`tabSales Person\`
                    WHERE custom_head_sales_code IS NOT NULL
                    AND custom_head_sales_code != ''
                    AND custom_head_sales_code LIKE %s
                `, ["%" + txt + "%"]);
            }
        },

        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },

        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group"
        },

        {
            fieldname: "custom_main_group",
            label: "Category",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_main_group
                    FROM \`tabItem\`
                    WHERE custom_main_group IS NOT NULL
                    AND custom_main_group != ''
                    AND custom_main_group LIKE %s
                `, ["%" + txt + "%"]);
            }
        }

    ]
};