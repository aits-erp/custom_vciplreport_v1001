frappe.query_reports["TSO WISE CATEGORYWISE"] = {

    onload: async function(report) {
        const result = await frappe.db.get_list("Item", {
            fields: ["custom_main_group"],
            filters: [["custom_main_group", "!=", ""]],
            group_by: "custom_main_group",
            limit: 0
        });

        const groups = [...new Set(
            result.map(r => r.custom_main_group).filter(Boolean)
        )].sort();

        report.set_filter_value("custom_main_group", groups);
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
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "custom_region",
            label: "Region",
            fieldtype: "MultiSelectList",
            get_data: async function(txt) {
                const rows = await frappe.db.get_list("Sales Person", {
                    fields: ["custom_region"],
                    filters: [
                        ["custom_region", "!=", ""],
                        ["custom_region", "like", "%" + txt + "%"]
                    ],
                    group_by: "custom_region",
                    limit: 50
                });
                return [...new Set(rows.map(r => r.custom_region).filter(Boolean))].sort()
                    .map(v => ({ label: v, value: v }));
            }
        },    
        {
            fieldname: "custom_head_sales_code",
            label: "Head Sales Code",
            fieldtype: "MultiSelectList",
            get_data: async function(txt) {
                const rows = await frappe.db.get_list("Sales Person", {
                    fields: ["custom_head_sales_code"],
                    filters: [
                        ["custom_head_sales_code", "!=", ""],
                        ["custom_head_sales_code", "like", "%" + txt + "%"]
                    ],
                    group_by: "custom_head_sales_code",
                    limit: 50
                });
                return [...new Set(rows.map(r => r.custom_head_sales_code).filter(Boolean))].sort()
                    .map(v => ({ label: v, value: v }));
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
            options: "Customer Group",
            default: "Debtors Distributors"
        },
        {
            fieldname: "custom_main_group",
            label: "Category",
            fieldtype: "MultiSelectList",
            get_data: async function(txt) {
                const rows = await frappe.db.get_list("Item", {
                    fields: ["custom_main_group"],
                    filters: [
                        ["custom_main_group", "!=", ""],
                        ["custom_main_group", "like", "%" + txt + "%"]
                    ],
                    group_by: "custom_main_group",
                    limit: 100
                });
                return [...new Set(rows.map(r => r.custom_main_group).filter(Boolean))].sort()
                    .map(v => ({ label: v, value: v }));
            }
        },
        {
            fieldname: "show_item_details",
            label: "Include Item Code & Item Name",
            fieldtype: "Check",
            default: 0
        }
    ]
};