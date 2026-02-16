// frappe.query_reports["Item Category Wise - Report"] = {
//     filters: [
//         {
//             fieldname: "from_date",
//             label: "From Date",
//             fieldtype: "Date",
//             default: frappe.sys_defaults.year_start_date,
//             reqd: 1
//         },
//         {
//             fieldname: "to_date",
//             label: "To Date",
//             fieldtype: "Date",
//             default: frappe.sys_defaults.year_end_date,
//             reqd: 1
//         },
//         {
//             fieldname: "item_group",
//             label: "Item Group",
//             fieldtype: "Link",
//             options: "Item Group"
//         },
//         {
//             fieldname: "parent_sales_person",
//             label: "Parent Sales Person",
//             fieldtype: "Link",
//             options: "Sales Person"
//         },
//         {
//             fieldname: "customer",
//             label: "Customer",
//             fieldtype: "Link",
//             options: "Customer"
//         },
//         {
//             fieldname: "custom_main_group",
//             label: "Main Group",
//             fieldtype: "Data"
//         },
//         {
//             fieldname: "custom_sub_group",
//             label: "Sub Group",
//             fieldtype: "Data"
//         },
//         {
//             fieldname: "custom_item_type",
//             label: "Item Type",
//             fieldtype: "Data"
//         }
//     ]
// };


frappe.query_reports["Item Category Wise - Report"] = {

    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data) return value;

        if (["item_group","custom_main_group","custom_sub_group"]
            .includes(column.fieldname)) return value;

        if (value && column.fieldtype === "Currency") {
            return `<a class="customer-link"
                        data-customer="${column.label}"
                        style="font-weight:600; cursor:pointer;">
                        ${value}
                    </a>`;
        }

        return value;
    },

    onload: function(report) {

        report.page.wrapper.on("click", ".customer-link", function() {

            let customer = $(this).data("customer");
            let filters = report.get_values();

            frappe.call({
                method: "your_app.your_module.report.item_category_wise_report.get_customer_summary",
                args: {
                    customer: customer,
                    from_date: filters.from_date,
                    to_date: filters.to_date
                },
                callback: function(r) {

                    let d = new frappe.ui.Dialog({
                        title: "Customer Summary",
                        fields: [
                            {label:"Customer", fieldtype:"Data", default:r.message.customer},
                            {label:"Target", fieldtype:"Currency", default:r.message.target},
                            {label:"Invoice", fieldtype:"Currency", default:r.message.invoice},
                            {label:"Achieved %", fieldtype:"Percent", default:r.message.achieved},
                            {label:"Last Year", fieldtype:"Currency", default:r.message.last_year},
                        ]
                    });

                    d.show();
                }
            });

        });
    }
};
