frappe.query_reports["Distributors Reportss"] = {

    filters: [
        {
            fieldname: "parent_sales_person",
            label: __("Parent Sales Person"),
            fieldtype: "Link",
            options: "Sales Person",
            reqd: 1
        },
        {
            fieldname: "custom_territory",
            label: __("Territory"),
            fieldtype: "Link",
            options: "Territory",
            reqd: 1
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data.indent === 0) value = `<b>${value}</b>`;
        if (data.indent === 1) value = `<b>${value}</b>`;
        if (data.indent === 2) value = `<i>${value}</i>`;

        return value;
    }
};
