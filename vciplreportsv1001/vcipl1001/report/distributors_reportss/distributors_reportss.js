frappe.query_reports["Distributor Sales Hierarchy"] = {

    filters: [
        {
            fieldname: "parent_sales_person",
            label: __("Parent Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data && data.indent === 0) {
            value = `<b>${value}</b>`;
        }
        if (data && data.indent === 1) {
            value = `<i>${value}</i>`;
        }

        return value;
    }
};
