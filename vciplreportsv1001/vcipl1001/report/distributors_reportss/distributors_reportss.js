frappe.query_reports["Distributors Reportss"] = {
    tree: true,
    initial_depth: 1,

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Highlight customer rows
        if (data.indent === 4 && column.fieldname === "name") {
            value = `<span style="color:#1674E0;font-weight:bold">${value}</span>`;
        }

        // Bold amounts at customer level
        if (data.indent === 4 && column.fieldname === "amount") {
            value = `<b>${value}</b>`;
        }

        return value;
    }
};
