// frappe.query_reports["SALES ORDER FILL RATIO"] = {

//     filters: [
//         { fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company", default: frappe.defaults.get_user_default("Company"), reqd: 1 },
//         { fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
//         { fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
//         { fieldname: "warehouse", label: __("Warehouse"), fieldtype: "Link", options: "Warehouse" },
//         { fieldname: "group_by_so", label: __("Group by Sales Order"), fieldtype: "Check", default: 1 }
//     ],

//     formatter(value, row, column, data, default_formatter) {

//         value = default_formatter(value, row, column, data);

//         if (column.fieldname === "pending_delivery") {
//             return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
//                 onclick='frappe.query_reports["SALES ORDER FILL RATIO"]
//                 .show_popup(${data.pending_popup}, "${data.customer}", "${data.sales_order}")'>
//                 View Items
//             </a>`;
//         }

//         return value;
//     },

//     show_popup(data, customer, sales_order) {

//         let rows = data.items || [];
//         let totals = data.totals || {};

//         let html = `
//         <div id="pending-popup">

//         <h3>Sales Order Fill Ratio</h3>
//         <h4>Customer: ${customer}</h4>
//         <h5>Sales Order: ${sales_order}</h5>

//         <table class="table table-bordered">
//         <tr>
//             <th>Item</th>
//             <th>Ordered</th>
//             <th>Delivered</th>
//             <th>Pending</th>
//             <th>Available</th>
//             <th>Fill %</th>
//             <th>Date</th>
//         </tr>`;

//         rows.forEach(r => {
//             html += `
//             <tr>
//                 <td>${r.item_name}</td>
//                 <td>${r.ordered_qty}</td>
//                 <td>${r.delivered_qty}</td>
//                 <td>${r.pending_qty}</td>
//                 <td>${r.available_qty}</td>
//                 <td>${r.ratio}%</td>
//                 <td>${r.delivery_date}</td>
//             </tr>`;
//         });

//         html += `
//         <tr style="font-weight:bold;background:#f3f3f3">
//             <td>Grand Total</td>
//             <td>${totals.ordered}</td>
//             <td>${totals.delivered}</td>
//             <td>${totals.pending}</td>
//             <td colspan="3"></td>
//         </tr>
//         </table>

//         <br>
//         <button class="btn btn-primary" onclick="print_pending_popup()">🖨 Print / Save PDF</button>

//         </div>`;

//         frappe.msgprint({
//             title: "Item Level Details",
//             message: html,
//             wide: true
//         });
//     }
// };


// window.print_pending_popup = function () {

//     let content = document.getElementById("pending-popup").innerHTML;

//     let w = window.open("", "", "width=900,height=700");

//     w.document.write(`
//         <html>
//         <head>
//             <title>Sales Order Fill Ratio</title>
//             <style>
//                 body { font-family: Arial; padding: 20px; }
//                 table { border-collapse: collapse; width: 100%; }
//                 table, th, td { border: 1px solid black; padding: 6px; text-align:center; }
//                 h3,h4,h5 { margin: 5px 0; }
//             </style>
//         </head>
//         <body>
//             ${content}
//         </body>
//         </html>
//     `);

//     w.document.close();
//     w.focus();
//     w.print();
// };

frappe.query_reports["SALES ORDER FILL RATIO"] = {

    filters: [
        { fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company", default: frappe.defaults.get_user_default("Company"), reqd: 1 },
        { fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
        { fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
        { fieldname: "warehouse", label: __("Warehouse"), fieldtype: "Link", options: "Warehouse" },
        { fieldname: "group_by_so", label: __("Group by Sales Order"), fieldtype: "Check", default: 1 }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "pending_delivery" && data.pending_popup) {

            let safe_json = encodeURIComponent(data.pending_popup);

            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["SALES ORDER FILL RATIO"]
                .show_popup("${safe_json}", "${data.customer}", "${data.sales_order}")'>
                View Items
            </a>`;
        }

        return value;
    },

    show_popup(encoded_data, customer, sales_order) {

        let data = JSON.parse(decodeURIComponent(encoded_data));
        let rows = data.items || [];
        let totals = data.totals || {};

        let html = `
        <div id="pending-popup">

        <h3>Sales Order Fill Ratio</h3>
        <h4>Customer: ${customer}</h4>
        <h5>Sales Order: ${sales_order}</h5>

        <div style="max-height:500px;overflow:auto">
        <table class="table table-bordered">
        <thead style="position:sticky;top:0;background:white">
        <tr>
            <th>Item</th>
            <th>Ordered</th>
            <th>Delivered</th>
            <th>Pending</th>
            <th>Available</th>
            <th>Fill %</th>
            <th>Date</th>
        </tr>
        </thead>
        <tbody>`;

        rows.forEach(r => {
            html += `
            <tr>
                <td>${r.item_name}</td>
                <td>${r.ordered_qty}</td>
                <td>${r.delivered_qty}</td>
                <td>${r.pending_qty}</td>
                <td>${r.available_qty}</td>
                <td>${r.ratio}%</td>
                <td>${r.delivery_date}</td>
            </tr>`;
        });

        html += `
        <tr style="font-weight:bold;background:#f3f3f3">
            <td>Grand Total</td>
            <td>${totals.ordered}</td>
            <td>${totals.delivered}</td>
            <td>${totals.pending}</td>
            <td colspan="3"></td>
        </tr>
        </tbody>
        </table>
        </div>

        <br>
        <button class="btn btn-primary" onclick="print_pending_popup()">🖨 Print / Save PDF</button>

        </div>`;

        let d = new frappe.ui.Dialog({
            title: "Item Level Details",
            fields: [{ fieldtype: "HTML", fieldname: "html" }]
        });

        d.fields_dict.html.$wrapper.html(html);
        d.show();

        // 🔥 make dialog wide
        d.$wrapper.find('.modal-dialog').css({
            "max-width": "95%",
            "width": "95%"
        });
    }
};

window.print_pending_popup = function () {

    let content = document.getElementById("pending-popup").innerHTML;

    let w = window.open("", "", "width=1000,height=800");

    w.document.write(`
        <html>
        <head>
            <title>Sales Order Fill Ratio</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid black; padding: 6px; text-align:center; }
                h3,h4,h5 { margin: 5px 0; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);

    w.document.close();
    w.focus();
    w.print();
};
