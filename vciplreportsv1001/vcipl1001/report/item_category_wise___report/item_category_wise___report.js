frappe.query_reports["Item Category Wise - Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.sys_defaults.year_start_date,
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.sys_defaults.year_end_date,
            reqd: 1
        },
        {
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group"
        },
        {
            fieldname: "parent_sales_person",
            label: "Parent Sales Person",
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
            fieldname: "custom_main_group",
            label: "Main Group",
            fieldtype: "Data"
        },
        {
            fieldname: "custom_sub_group",
            label: "Sub Group",
            fieldtype: "Data"
        },
        {
            fieldname: "custom_item_type",
            label: "Item Type",
            fieldtype: "Data"
        }
    ]
};
