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
            default: frappe.sys_defaults.year_start_date,
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.sys_defaults.year_end_date,
            reqd: 1
        },
        {
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group"
        },
        {
            fieldname: "parent_sales_person",
            label: "Parent Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "custom_main_group",
            label: "Main Group",
            fieldtype: "Data"
        },
        {
            fieldname: "custom_sub_group",
            label: "Sub Group",
            fieldtype: "Data"
        },
        {
            fieldname: "custom_item_type",
            label: "Item Type",
            fieldtype: "Data"
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        // skip group columns
        if (["item_group", "custom_main_group", "custom_sub_group"].includes(column.fieldname)) {
            return value;
        }

        // clickable amount
        if (data[column.fieldname] > 0) {
            value = `<a href="javascript:void(0)"
                onclick="show_customer_items('${column.label}',
                '${data.item_group}',
                '${data.custom_main_group}',
                '${data.custom_sub_group}')">
                ${value}
            </a>`;
        }

        return value;
    }
};


// ---------------- POPUP FUNCTION ----------------
window.show_customer_items = function(customer, item_group, main_group, sub_group) {

    frappe.call({
        method: "vciplreportsv1001.vcipl1001.report.item_category_wise__report.item_category_wise__report.get_customer_items",
        args: {
            customer: customer,
            item_group: item_group,
            main_group: main_group,
            sub_group: sub_group
        },
        callback: function(r) {

            let d = new frappe.ui.Dialog({
                title: `Items sold to ${customer}`,
                size: "large",
                fields: [{ fieldtype: "HTML", fieldname: "items_html" }]
            });

            let html = `
                <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Invoice</th>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Amount</th>
                    </tr>
                </thead><tbody>
            `;

            r.message.forEach(row => {
                html += `
                    <tr>
                        <td>
                            <a href="/app/sales-invoice/${row.invoice}" target="_blank">
                                ${row.invoice}
                            </a>
                        </td>
                        <td>${row.item_name}</td>
                        <td>${row.qty}</td>
                        <td>${row.amount}</td>
                    </tr>
                `;
            });

            html += "</tbody></table>";

            d.fields_dict.items_html.$wrapper.html(html);
            d.show();
        }
    });
};
