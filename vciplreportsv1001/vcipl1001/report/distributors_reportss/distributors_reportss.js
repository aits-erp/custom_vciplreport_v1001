frappe.query_reports["Distributors Reportss"] = {
    tree: true,
    initial_depth: 1,

    filters: [
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: [
                { label: "January", value: 1 },
                { label: "February", value: 2 },
                { label: "March", value: 3 },
                { label: "April", value: 4 },
                { label: "May", value: 5 },
                { label: "June", value: 6 },
                { label: "July", value: 7 },
                { label: "August", value: 8 },
                { label: "September", value: 9 },
                { label: "October", value: 10 },
                { label: "November", value: 11 },
                { label: "December", value: 12 }
            ],
            default: new Date().getMonth() + 1
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.sys_defaults.year_start_date
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.sys_defaults.year_end_date
        }
    ],

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Parent Sales Person
        if (data.indent === 3 && column.fieldname === "name") {
            value = `<b>${value}</b>`;
        }

        // Customer highlight
        if (data.indent === 5 && column.fieldname === "name") {
            value = `<span style="color:#1674E0;font-weight:bold">${value}</span>`;
        }

        // Bold target & amount at customer level
        if (data.indent === 5 && ["target", "amount"].includes(column.fieldname)) {
            value = `<b>${value}</b>`;
        }

        return value;
    }
};
