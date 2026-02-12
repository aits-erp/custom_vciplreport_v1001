// frappe.query_reports["Monthwise Sales Report"] = {
//     filters: [
//         {
//             fieldname: "month",
//             label: __("Month"),
//             fieldtype: "Select",
//             options: [
//                 "",
//                 "January","February","March",
//                 "April","May","June",
//                 "July","August","September",
//                 "October","November","December"
//             ]
//         }
//     ],

//     formatter(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);

//         if (
//             column.fieldtype === "Currency" &&
//             data &&
//             data[column.fieldname + "_drill"] &&
//             value
//         ) {
//             return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
//                 onclick='frappe.query_reports["Monthwise Sales Report"]
//                 .show_popup(${data[column.fieldname + "_drill"]}, "${column.label}")'>
//                 ${value}
//             </a>`;
//         }

//         return value;
//     },

//     show_popup(rows, title) {
//         if (!rows || rows.length === 0) {
//             frappe.msgprint(__("No Sales Invoices"));
//             return;
//         }

//         let html = `
//         <div style="max-height:500px;overflow:auto">
//         <table class="table table-bordered">
//             <thead>
//                 <tr>
//                     <th>Sales Invoice</th>
//                     <th>Date</th>
//                     <th>Amount</th>
//                 </tr>
//             </thead><tbody>`;

//         rows.forEach(r => {
//             html += `
//             <tr>
//                 <td>
//                     <a href="/app/sales-invoice/${r.invoice}"
//                        target="_blank"
//                        style="font-weight:bold">
//                        ${r.invoice}
//                     </a>
//                 </td>
//                 <td>${r.date}</td>
//                 <td>${format_currency(r.amount)}</td>
//             </tr>`;
//         });

//         html += `</tbody></table></div>`;

//         frappe.msgprint({
//             title: title,
//             message: html,
//             wide: true
//         });
//     }
// };

frappe.query_reports["Monthwise Sales Report"] = {
    filters: [
        {
            fieldname: "customer_group",
            label: __("Customer Group"),
            fieldtype: "Link",
            options: "Customer Group"
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                "",
                "January","February","March",
                "April","May","June",
                "July","August","September",
                "October","November","December"
            ]
        }
    ],

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (
            column.fieldtype === "Currency" &&
            data &&
            data[column.fieldname + "_drill"] &&
            value
        ) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Monthwise Sales Report"]
                .show_popup(${data[column.fieldname + "_drill"]}, "${column.label}")'>
                ${value}
            </a>`;
        }

        return value;
    },

    show_popup(rows, title) {
        if (!rows || rows.length === 0) {
            frappe.msgprint(__("No Sales Invoices"));
            return;
        }

        let html = `
        <div style="max-height:500px;overflow:auto">
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Sales Invoice</th>
                    <th>Date</th>
                    <th>Amount</th>
                </tr>
            </thead><tbody>`;

        rows.forEach(r => {
            html += `
            <tr>
                <td>
                    <a href="/app/sales-invoice/${r.invoice}"
                       target="_blank"
                       style="font-weight:bold">
                       ${r.invoice}
                    </a>
                </td>
                <td>${r.date}</td>
                <td>${format_currency(r.amount)}</td>
            </tr>`;
        });

        html += `</tbody></table></div>`;

        frappe.msgprint({
            title: title,
            message: html,
            wide: true
        });
    }
};