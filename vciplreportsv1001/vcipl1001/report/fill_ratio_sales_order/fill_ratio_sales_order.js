frappe.query_reports["FILL RATIO SALES ORDER"] = {

    filters: [

        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
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
        },

        {
            fieldname: "risk_filter",
            label: __("Risk Level"),
            fieldtype: "Select",
            options: ["", "HIGH", "Medium", "OK"],
            default: ""
        }

    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "risk") {

            if (data.risk === "Critical") {
                value = `<span style="color:red;font-weight:bold">🔴 HIGH</span>`;
            }

            if (data.risk === "Warning") {
                value = `<span style="color:orange;font-weight:bold">🟠 Medium</span>`;
            }

            if (data.risk === "OK") {
                value = `<span style="color:green;font-weight:bold">🟢 OK</span>`;
            }
        }

        if (column.fieldname === "fill_ratio") {

            if (data.fill_ratio < 50) {
                value = `<span style="color:red;font-weight:bold">${data.fill_ratio}%</span>`;
            } else if (data.fill_ratio < 80) {
                value = `<span style="color:orange;font-weight:bold">${data.fill_ratio}%</span>`;
            } else {
                value = `<span style="color:green;font-weight:bold">${data.fill_ratio}%</span>`;
            }
        }

        return value;
    }
};
