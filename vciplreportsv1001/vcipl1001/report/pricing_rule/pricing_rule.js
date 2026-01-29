frappe.query_reports["Customer Pricing Rule Report"] = {
    filters: [
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "apply_on",
            label: __("Apply On"),
            fieldtype: "Select",
            options: ["", "Item Code", "Item Group", "Brand"]
        },
        {
            fieldname: "enabled",
            label: __("Enabled"),
            fieldtype: "Check",
            default: 1
        }
    ]
};
