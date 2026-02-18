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
//     ],

//     formatter(value, row, column, data, default_formatter) {

//         value = default_formatter(value, row, column, data);

//         if (!data) return value;

//         if (["item_group", "custom_main_group", "custom_sub_group"].includes(column.fieldname)) {
//             return value;
//         }

//         if (data[column.fieldname] > 0) {
//             value = `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
//                 onclick='frappe.query_reports["Item Category Wise - Report"]
//                 .show_popup("${column.fieldname}", ${data.popup_data})'>
//                 ${value}
//             </a>`;
//         }

//         return value;
//     },

//     show_popup(customer_field, popup_data) {

//         let rows = popup_data[customer_field] || [];

//         let html = `
//         <div>
//         <table class="table table-bordered">
//         <tr>
//             <th>Invoice</th>
//             <th>Item</th>
//             <th>Qty</th>
//             <th>Amount</th>
//         </tr>`;

//         rows.forEach(r => {
//             html += `
//             <tr>
//                 <td><a href="/app/sales-invoice/${r.invoice}" target="_blank">${r.invoice}</a></td>
//                 <td>${r.item_name}</td>
//                 <td>${r.qty}</td>
//                 <td>${r.amount}</td>
//             </tr>`;
//         });

//         html += `</table></div>`;

//         frappe.msgprint({
//             title: "Item Breakdown",
//             message: html,
//             wide: true
//         });
//     }
// };

frappe.query_reports["Item Category Wise - Report"] = {

    filters: [
        { fieldname: "from_date", label: "From Date", fieldtype: "Date", default: frappe.sys_defaults.year_start_date, reqd: 1 },
        { fieldname: "to_date", label: "To Date", fieldtype: "Date", default: frappe.sys_defaults.year_end_date, reqd: 1 },
        { fieldname: "item_group", label: "Item Group", fieldtype: "Link", options: "Item Group" },
        { fieldname: "parent_sales_person", label: "Parent Sales Person", fieldtype: "Link", options: "Sales Person" },
        { fieldname: "customer", label: "Customer", fieldtype: "Link", options: "Customer" },
        { fieldname: "custom_main_group", label: "Main Group", fieldtype: "Data" },
        { fieldname: "custom_sub_group", label: "Sub Group", fieldtype: "Data" },
        { fieldname: "custom_item_type", label: "Item Type", fieldtype: "Data" }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        if (["item_group", "custom_main_group", "custom_sub_group"].includes(column.fieldname)) {
            return value;
        }

        if (data[column.fieldname] > 0) {
            value = `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Item Category Wise - Report"]
                .show_popup("${column.fieldname}", ${data.popup_data})'>
                ${value}
            </a>`;
        }

        return value;
    },

    show_popup(customer_field, popup_data) {

        let rows = popup_data[customer_field] || [];

        let html = `
        <div>
        <table class="table table-bordered">
        <tr>
            <th>Item</th>
            <th>Qty</th>
            <th>Amount</th>
        </tr>`;

        rows.forEach(r => {
            let bold = r.item_name.includes("Total") ? "font-weight:bold;background:#f7f7f7" : "";

            html += `
            <tr style="${bold}">
                <td>${r.item_name}</td>
                <td>${r.qty}</td>
                <td>${r.amount}</td>
            </tr>`;
        });

        html += `</table></div>`;

        frappe.msgprint({
            title: "Item Breakdown",
            message: html,
            wide: true
        });
    }
};
