// frappe.query_reports["Pending Sales Order Report"] = {

//     filters: [
//         {
//             fieldname: "company",
//             label: __("Company"),
//             fieldtype: "Link",
//             options: "Company",
//             default: frappe.defaults.get_user_default("Company"),
//             reqd: 1
//         },

//         {
//             fieldname: "from_date",
//             label: __("From Date"),
//             fieldtype: "Date",
//             default: frappe.datetime.year_start()
//         },

//         {
//             fieldname: "to_date",
//             label: __("To Date"),
//             fieldtype: "Date",
//             default: frappe.datetime.year_end()
//         },

//         {
//             fieldname: "sales_order",
//             label: __("Sales Order"),
//             fieldtype: "MultiSelectList",
//             options: "Sales Order",
//             get_data(txt) {
//                 return frappe.db.get_link_options("Sales Order", txt);
//             }
//         },

//         { fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },

//         {
//             fieldname: "status",
//             label: __("Status"),
//             fieldtype: "MultiSelectList",
//             default: ["To Deliver and Bill"]
//         },

//         { fieldname: "warehouse", label: __("Warehouse"), fieldtype: "Link", options: "Warehouse" },

//         { fieldname: "group_by_so", label: __("Group by Sales Order"), fieldtype: "Check", default: 1 }
//     ],

//     formatter(value, row, column, data, default_formatter) {

//         value = default_formatter(value, row, column, data);

//         if (column.fieldname === "pending_qty" && data?.pending_qty > 0) {
//             value = `<span style="color:red;font-weight:600">${value}</span>`;
//         }

//         if (column.fieldname === "pending_delivery") {
//             return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
//                 onclick='frappe.query_reports["Pending Sales Order Report"]
//                 .show_popup(${data.pending_popup}, "${data.customer}", "${data.sales_order}")'>
//                 View Pending
//             </a>`;
//         }

//         return value;
//     },

//     show_popup(rows, customer, sales_order) {

//         let html = `
//         <div id="pending-popup">

//         <h4>Customer: ${customer}</h4>
//         <h5>Sales Order: ${sales_order}</h5>

//         <div id="print-container">
//         <table class="table table-bordered">
//         <tr>
//             <th>Item Code</th>   <!-- ✅ ADDED -->
//             <th>Item Name</th>
//             <th>Pending</th>
//             <th>Available</th>
//             <th>Date</th>
//         </tr>`;

//         rows.forEach(r => {

//             if (r.pending_qty <= 0) return;

//             html += `
//             <tr>
//                 <td>${r.item_code}</td> <!-- ✅ ADDED -->
//                 <td>${r.item_name}</td>
//                 <td style="color:red;font-weight:bold">${r.pending_qty}</td>
//                 <td style="color:green;font-weight:bold">${r.available_qty}</td>
//                 <td>${r.delivery_date}</td>
//             </tr>`;
//         });

//         html += `
//         </table>
//         </div>

//         <button class="btn btn-primary" onclick="print_pending_popup()">Print</button>
//         </div>`;

//         frappe.msgprint({
//             title: "Pending Items",
//             message: html,
//             wide: true
//         });
//     }
// };


// window.print_pending_popup = function () {

//     let popup = document.getElementById("pending-popup").cloneNode(true);

//     let btn = popup.querySelector("button");
//     if (btn) btn.remove();

//     let content = popup.outerHTML;

//     let w = window.open("", "_blank");

//     w.document.open();

//     w.document.write(`
//         <!DOCTYPE html>
//         <html>
//         <head>
//             <title>Pending Items</title>

//             <style>

//                 @page {
//                     size: A4;
//                     margin: 10mm;
//                 }

//                 body{
//                     font-family: Arial, sans-serif;
//                     margin:0;
//                     width:100%;
//                 }

//                 h4{
//                     margin-bottom:5px;
//                 }

//                 h5{
//                     margin-top:0;
//                     margin-bottom:15px;
//                 }

//                 table{
//                     width:100%;
//                     border-collapse:collapse;
//                     table-layout:auto;
//                 }

//                 th, td{
//                     border:1px solid black;
//                     padding:8px;
//                     text-align:left;
//                     word-wrap:break-word;
//                 }

//                 th{
//                     background:#f2f2f2;
//                 }

//             @media print{

//                 body{
//                     width:100%;
//                 }

//                 #print-container{
//                     max-height: none !important;
//                     overflow: visible !important;
//                 }

//                 table{
//                     width:100%;
//                     border-collapse: collapse;
//                 }

//                 tr{
//                     page-break-inside: avoid;
//                 }

//                 thead{
//                     display: table-header-group;
//                 }

//             }

//             </style>

//         </head>

//         <body>

//         ${content}

//         </body>
//         </html>
//     `);

//     w.document.close();

//     w.onload = function () {
//         w.focus();
//         w.print();
//     };
// };


frappe.query_reports["Pending Sales Order Report"] = {

    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_start()
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_end()
        },

        {
            fieldname: "sales_order",
            label: __("Sales Order"),
            fieldtype: "MultiSelectList",
            options: "Sales Order",
            get_data(txt) {
                return frappe.db.get_link_options("Sales Order", txt);
            }
        },

        { fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },

        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "MultiSelectList",
            default: ["To Deliver and Bill"]
        },

        { fieldname: "warehouse", label: __("Warehouse"), fieldtype: "Link", options: "Warehouse" },

        { fieldname: "group_by_so", label: __("Group by Sales Order"), fieldtype: "Check", default: 1 }
    ],

    // Cache row data in memory, keyed by a safe generated string.
    // We NEVER embed raw customer/item text (which may contain apostrophes,
    // quotes, etc. e.g. "Chef's Lagan") into an onclick attribute anymore.
    _pending_cache: {},
    _pending_key_counter: 0,

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "pending_qty" && data?.pending_qty > 0) {
            value = `<span style="color:red;font-weight:600">${value}</span>`;
        }

        if (column.fieldname === "pending_delivery") {

            let report = frappe.query_reports["Pending Sales Order Report"];
            report._pending_key_counter += 1;
            let key = "row_" + report._pending_key_counter;

            report._pending_cache[key] = {
                rows: data.pending_popup,
                customer: data.customer,
                sales_order: data.sales_order
            };

            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Pending Sales Order Report"].show_popup_by_key("${key}")'>
                View Pending
            </a>`;
        }

        return value;
    },

    show_popup_by_key(key) {
        let cached = frappe.query_reports["Pending Sales Order Report"]._pending_cache[key];

        if (!cached) {
            frappe.msgprint(__("Could not load pending data for this row."));
            return;
        }

        // cached.rows comes from Python's frappe.as_json(), so it is a
        // JSON string, not an array yet - parse it here before use.
        let rows = cached.rows;
        if (typeof rows === "string") {
            try {
                rows = JSON.parse(rows);
            } catch (e) {
                console.error("Failed to parse pending_popup JSON", e);
                rows = [];
            }
        }

        frappe.query_reports["Pending Sales Order Report"].show_popup(
            rows, cached.customer, cached.sales_order
        );
    },

    show_popup(rows, customer, sales_order) {

        // Escape every dynamic value before inserting into HTML so that
        // apostrophes, quotes, &, <, > in customer/item names never break
        // the popup markup either.
        const esc = (val) => frappe.utils.escape_html(val == null ? "" : String(val));

        let html = `
        <div id="pending-popup">

        <h4>Customer: ${esc(customer)}</h4>
        <h5>Sales Order: ${esc(sales_order)}</h5>

        <div id="print-container">
        <table class="table table-bordered">
        <tr>
            <th>Item Code</th>
            <th>Item Name</th>
            <th>Pending</th>
            <th>Available</th>
            <th>Date</th>
        </tr>`;

        rows.forEach(r => {

            if (r.pending_qty <= 0) return;

            html += `
            <tr>
                <td>${esc(r.item_code)}</td>
                <td>${esc(r.item_name)}</td>
                <td style="color:red;font-weight:bold">${esc(r.pending_qty)}</td>
                <td style="color:green;font-weight:bold">${esc(r.available_qty)}</td>
                <td>${esc(r.delivery_date)}</td>
            </tr>`;
        });

        html += `
        </table>
        </div>

        <button class="btn btn-primary" onclick="print_pending_popup()">Print</button>
        </div>`;

        frappe.msgprint({
            title: "Pending Items",
            message: html,
            wide: true
        });
    }
};


window.print_pending_popup = function () {

    let popup = document.getElementById("pending-popup").cloneNode(true);

    let btn = popup.querySelector("button");
    if (btn) btn.remove();

    let content = popup.outerHTML;

    let w = window.open("", "_blank");

    w.document.open();

    w.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pending Items</title>

            <style>

                @page {
                    size: A4;
                    margin: 10mm;
                }

                body{
                    font-family: Arial, sans-serif;
                    margin:0;
                    width:100%;
                }

                h4{
                    margin-bottom:5px;
                }

                h5{
                    margin-top:0;
                    margin-bottom:15px;
                }

                table{
                    width:100%;
                    border-collapse:collapse;
                    table-layout:auto;
                }

                th, td{
                    border:1px solid black;
                    padding:8px;
                    text-align:left;
                    word-wrap:break-word;
                }

                th{
                    background:#f2f2f2;
                }

            @media print{

                body{
                    width:100%;
                }

                #print-container{
                    max-height: none !important;
                    overflow: visible !important;
                }

                table{
                    width:100%;
                    border-collapse: collapse;
                }

                tr{
                    page-break-inside: avoid;
                }

                thead{
                    display: table-header-group;
                }

            }

            </style>

        </head>

        <body>

        ${content}

        </body>
        </html>
    `);

    w.document.close();

    w.onload = function () {
        w.focus();
        w.print();
    };
};


