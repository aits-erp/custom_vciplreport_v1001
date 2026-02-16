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

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "pending_qty" && data?.pending_qty > 0) {
            value = `<span style="color:red;font-weight:600">${value}</span>`;
        }

        if (column.fieldname === "pending_delivery") {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Pending Sales Order Report"]
                .show_popup(${data.pending_popup}, "${data.customer}", "${data.sales_order}")'>
                View Pending
            </a>`;
        }

        return value;
    },

    show_popup(rows, customer, sales_order) {

        let html = `
        <div id="pending-popup">

        <h4>Customer: ${customer}</h4>
        <h5>Sales Order: ${sales_order}</h5>

        <div style="max-height:450px;overflow:auto">
        <table class="table table-bordered">
        <tr>
            <th>Item Name</th>
            <th>Pending</th>
            <th>Available</th>
            <th>Date</th>
        </tr>`;

        rows.forEach(r => {

            if (r.pending_qty <= 0) return;

            html += `
            <tr>
                <td>${r.item_name}</td>
                <td style="color:red;font-weight:bold">${r.pending_qty}</td>
                <td style="color:green;font-weight:bold">${r.available_qty}</td>
                <td>${r.delivery_date}</td>
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

    let content = document.getElementById("pending-popup").innerHTML;

    let w = window.open("", "", "width=900,height=700");
    w.document.write(`
        <html>
        <head>
            <title>Pending Items</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid black; padding: 6px; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);

    w.document.close();
    w.print();
};
