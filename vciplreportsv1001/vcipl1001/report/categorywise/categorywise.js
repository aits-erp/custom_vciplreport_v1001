frappe.query_reports["CATEGORYWISE"] = {
    filters: [
        {
            fieldname: "fiscal_year",
            label: "Fiscal Year",
            fieldtype: "Link",
            options: "Fiscal Year",
            default: frappe.defaults.get_user_default("fiscal_year"),
            reqd: 1
        },
        {
            fieldname: "custom_main_group",
            label: "Main Group",
            fieldtype: "Data"
        },
        {
            fieldname: "parent_sales_person",
            label: "Parent Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        }
    ]
};