frappe.query_reports["Stock Report - Cumulative"] = {
    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data",
            default: "Finished Goods"
        }
    ]
};
