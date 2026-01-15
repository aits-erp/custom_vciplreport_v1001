frappe.query_reports["Sales Analytics Drill"] = {

    filters: [
        {
            fieldname: "mode",
            label: "Mode",
            fieldtype: "Select",
            options: ["Customer", "Item"],
            default: "Customer",
            reqd: 1
        },
        { fieldname: "level", hidden: 1 },
        { fieldname: "customer_group", hidden: 1 },
        { fieldname: "custom_sub_group", hidden: 1 },
        { fieldname: "customer", hidden: 1 },
        { fieldname: "item_group", hidden: 1 },
        { fieldname: "custom_main_group", hidden: 1 },
        { fieldname: "custom_sub_group1", hidden: 1 },
        { fieldname: "item_code", hidden: 1 }
    ],

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "label" && data.drill) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Sales Analytics Drill"]
                .drill(${data.drill})'>
                ${value}
            </a>`;
        }
        return value;
    },

    drill(filters) {
        frappe.query_report.filters.forEach(f => {
            if (filters[f.fieldname] !== undefined) {
                frappe.query_report.set_filter_value(f.fieldname, filters[f.fieldname]);
            }
        });
        frappe.query_report.refresh();
    }
};
