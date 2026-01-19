frappe.query_reports["Distributors Reportss"] = {

    tree: true,
    initial_depth: 1,

    filters: [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        // Highlight TSO rows
        if (data.indent === 3 && column.fieldname === "name") {
            value = `<b style="color:#1674E0">${value}</b>`;
        }

        // Bold amount at TSO level
        if (data.indent === 3 && column.fieldname === "amount") {
            value = `<b>${value}</b>`;
        }

        return value;
    }
};
