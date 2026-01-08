frappe.query_reports["Top Most Selling Items"] = {
    onload: function (report) {
        report.set_filter_value("custom_item_type", "Finished Goods");
        report.set_filter_value("record_limit", 50);
    },

    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data",
            default: "Finished Goods",
            reqd: 0
        },
        {
            fieldname: "record_limit",
            label: __("Top Records"),
            fieldtype: "Select",
            options: [
                { label: "Top 50", value: 50 },
                { label: "Top 100", value: 100 }
            ],
            default: 50,
            reqd: 1
        }
    ]
};
