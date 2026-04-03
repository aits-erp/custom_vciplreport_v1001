frappe.query_reports["TSO WISE CATEGORYWISE"] = {

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

        // 🔥 CATEGORY (UPDATED TO CUSTOM GROUP)
        {
            fieldname: "custom_group",
            label: "Category",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_group
                    FROM \`tabItem\`
                    WHERE custom_group IS NOT NULL
                    AND custom_group != ''
                    AND custom_group LIKE %s
                `, ["%" + txt + "%"]);
            }
        }

    ]
};