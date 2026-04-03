frappe.query_reports["Top Most Selling Items"] = {

    onload: function (report) {
        const today = frappe.datetime.get_today();
        const today_obj = frappe.datetime.str_to_obj(today);

        const year = today_obj.getMonth() > 2
            ? today_obj.getFullYear()
            : today_obj.getFullYear() - 1;

        // ✅ Default values
        report.set_filter_value("custom_item_type", "Finished Goods");
        report.set_filter_value("record_limit", 50);
        report.set_filter_value("from_date", `${year}-04-01`);
        report.set_filter_value("to_date", `${year + 1}-03-31`);
        report.set_filter_value("show_all_items", 0);
    },

    // ✅ FINAL FIX → Show only Item Code (no name)
    formatter: function (value, row, column, data, default_formatter) {

        // Apply default formatter first
        value = default_formatter(value, row, column, data);

        // 🔥 Override Item Code display
        if (column.fieldname === "item_code" && data) {
            return data.item_code || "";
        }

        return value;
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
            fieldname: "show_all_items",
            label: __("Show All Items"),
            fieldtype: "Check",
            default: 0
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
            reqd: 1,
            depends_on: "eval:!doc.show_all_items"
        }
    ]
};