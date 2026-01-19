// frappe.query_reports["Sales Person Target Report"] = {

//     filters: [
//         {
//             fieldname: "company",
//             label: "Company",
//             fieldtype: "Link",
//             options: "Company",
//             default: frappe.defaults.get_user_default("Company")
//         },
//         {
//             fieldname: "year",
//             label: "Year",
//             fieldtype: "Select",
//             options: ["2023", "2024", "2025"],
//             default: new Date().getFullYear().toString()
//         },
//         {
//             fieldname: "month",
//             label: "Month",
//             fieldtype: "Select",
//             options: [
//                 { label: "January", value: 1 },
//                 { label: "February", value: 2 },
//                 { label: "March", value: 3 },
//                 { label: "April", value: 4 },
//                 { label: "May", value: 5 },
//                 { label: "June", value: 6 },
//                 { label: "July", value: 7 },
//                 { label: "August", value: 8 },
//                 { label: "September", value: 9 },
//                 { label: "October", value: 10 },
//                 { label: "November", value: 11 },
//                 { label: "December", value: 12 },
//             ],
//             default: new Date().getMonth() + 1
//         }
//     ],

//     formatter(value, row, column, data, default_formatter) {

//         value = default_formatter(value, row, column, data);

//         if (column.fieldname === "achieved" && data.achieved_drill) {
//             return `
//                 <a style="font-weight:bold;color:#1674E0;cursor:pointer"
//                    onclick='frappe.query_reports["Sales Person Target Report"]
//                    .show_popup(${data.achieved_drill}, "Achievement Invoices")'>
//                     ${value}
//                 </a>`;
//         }

//         return value;
//     },

//     show_popup(rows, title) {

//         if (!rows || rows.length === 0) {
//             frappe.msgprint("No data available");
//             return;
//         }

//         let html = `
//         <div style="max-height:500px;overflow:auto">
//         <table class="table table-bordered">
//             <thead>
//                 <tr>
//                     <th>Invoice</th>
//                     <th>Date</th>
//                     <th>Amount</th>
//                 </tr>
//             </thead><tbody>`;

//         rows.forEach(r => {
//             html += `
//             <tr>
//                 <td>
//                     <a href="/app/sales-invoice/${r.invoice}"
//                        target="_blank">
//                         ${r.invoice}
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

frappe.query_reports["Sales Person Target Report"] = {
   
    filters: [
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: ["2023", "2024", "2025"],
            default: new Date().getFullYear().toString()
        },
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: [
                { label: "January", value: 1 },
                { label: "February", value: 2 },
                { label: "March", value: 3 },
                { label: "April", value: 4 },
                { label: "May", value: 5 },
                { label: "June", value: 6 },
                { label: "July", value: 7 },
                { label: "August", value: 8 },
                { label: "September", value: 9 },
                { label: "October", value: 10 },
                { label: "November", value: 11 },
                { label: "December", value: 12 }
            ],
            default: new Date().getMonth() + 1
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "achieved" && data.achieved_drill) {
            return `
                <a style="font-weight:bold;color:#1674E0;cursor:pointer"
                   onclick='frappe.query_reports["Sales Person Target Report"]
                   .show_popup(${data.achieved_drill}, "Achievement Invoices")'>
                    ${value}
                </a>`;
        }

        return value;
    },

    show_popup(rows, title) {

        if (!rows || rows.length === 0) {
            frappe.msgprint("No data available");
            return;
        }

        let html = `
        <div style="max-height:500px;overflow:auto">
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Invoice</th>
                    <th>Date</th>
                    <th>Amount</th>
                </tr>
            </thead><tbody>`;

        rows.forEach(r => {
            html += `
            <tr>
                <td>
                    <a href="/app/sales-invoice/${r.invoice}" target="_blank">
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
