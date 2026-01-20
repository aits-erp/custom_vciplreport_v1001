frappe.query_reports["Distributor Sales Hierarchy"] = {

    filters: [
        {
            fieldname: "parent_sales_person",
            label: __("Parent Sales Person"),
            fieldtype: "Link",
            options: "Sales Person",
            reqd: 1
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                "",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December"
            ],
            default: frappe.datetime.str_to_obj(frappe.datetime.get_today()).toLocaleString("default", { month: "long" })
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date"
        }
    ],

    onload: function (report) {
        // Optional: auto-refresh when parent sales person is selected
        report.page.fields_dict.parent_sales_person.df.onchange = function () {
            report.refresh();
        };
    },

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Bold Parent Sales Person
        if (data && data.indent === 0) {
            value = `<b>${value}</b>`;
        }

        // Italic Geography
        if (data && data.indent === 1) {
            value = `<i>${value}</i>`;
        }

        return value;
    }
};
