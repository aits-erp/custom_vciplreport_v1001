frappe.query_reports["Distributors Reportss"] = {
    filters: [
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group",
            default: "Distributor"
        },
        {
            fieldname: "region",
            label: "Region",
            fieldtype: "Select",
            options: ["", "North", "South", "East", "West"]
        },
        {
            fieldname: "tso",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person"
        }
    ]
};
