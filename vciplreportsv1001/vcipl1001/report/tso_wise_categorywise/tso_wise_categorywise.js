frappe.query_reports["TSO WISE CATEGORYWISE"] = {

    onload: function(report) {

        // 🔥 DEFAULT CATEGORY VALUES
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

        // 🔥 CATEGORY FILTER
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