frappe.query_reports["Sales Person Target Report"] = {
    filters: [
        {
            fieldname: "sales_person",
            label: "Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        }
    ],

    tree: true,
    name_field: "sales_person",
    parent_field: "parent_sales_person",
    initial_depth: 2
};
