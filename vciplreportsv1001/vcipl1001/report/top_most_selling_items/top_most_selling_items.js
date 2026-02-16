frappe.query_reports["Top Most Selling Items"] = {
    onload: function (report) {
        const today = frappe.datetime.get_today();
        const year = frappe.datetime.str_to_obj(today).getMonth() > 2
            ? frappe.datetime.str_to_obj(today).getFullYear()
            : frappe.datetime.str_to_obj(today).getFullYear() - 1;

        report.set_filter_value("custom_item_type", "Finished Goods");
        report.set_filter_value("record_limit", 50);
        report.set_filter_value("from_date", `${year}-04-01`);
        report.set_filter_value("to_date", `${year + 1}-03-31`);
    },

    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data",
            default: "Finished Goods"
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1
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
