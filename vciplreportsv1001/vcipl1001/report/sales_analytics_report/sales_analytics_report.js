frappe.query_reports["Sales Analytics – Drill Down"] = {

    filters: [
        {
            fieldname: "mode",
            label: "Mode",
            fieldtype: "Select",
            options: "Customer\nItem",
            default: "Customer"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.year_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.year_end()
        },
        {
            fieldname: "metric",
            label: "Metric",
            fieldtype: "Select",
            options: "Value\nQty",
            default: "Value"
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "name" && data.drill) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Sales Analytics – Drill Down"]
                .drill(${data.drill})'>${value}</a>`;
        }

        if (column.fieldname === "invoice") {
            return `<a href="/app/sales-invoice/${value}"
                target="_blank"
                style="font-weight:bold">${value}</a>`;
        }

        return value;
    },

    drill(args) {
        frappe.query_report.set_filter_value("level", args.level);

        if (args.value)
            frappe.query_report.set_filter_value("value", args.value);

        if (args.customer)
            frappe.query_report.set_filter_value("customer", args.customer);

        if (args.item_code)
            frappe.query_report.set_filter_value("item_code", args.item_code);

        frappe.query_report.refresh();
    }
};
