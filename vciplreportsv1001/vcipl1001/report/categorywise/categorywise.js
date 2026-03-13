frappe.query_reports["CATEGORYWISE"] = {
    filters: [

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