frappe.query_reports["Customer & Supplier Fill Ratio"] = {

    filters: [
        {
            fieldname: "party_type",
            label: __("Show Data For"),
            fieldtype: "Select",
            options: "Both\nCustomer\nSupplier",
            default: "Both",
            reqd: 1
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date"
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "pending_delivery" && data.pending_popup) {

            let safe = encodeURIComponent(data.pending_popup);

            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Customer & Supplier Fill Ratio"]
                .show_popup("${safe}", "${data.party}", "${data.order_id}")'>
                View Items
            </a>`;
        }

        return value;
    },

    show_popup(encoded_data, party, order_id) {

        let data = JSON.parse(decodeURIComponent(encoded_data));
        let rows = data.items || [];
        let totals = data.totals || {};

        let html = `
        <div id="pending-popup">
        <h3>Fill Ratio Details</h3>
        <h4>Party: ${party}</h4>
        <h5>Order: ${order_id}</h5>

        <table class="table table-bordered">
        <thead>
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
            <td>Total</td>
            <td>${totals.ordered}</td>
            <td>${totals.delivered}</td>
            <td>${totals.pending}</td>
            <td colspan="3"></td>
        </tr>
        </tbody></table>

        <button class="btn btn-primary" onclick="print_pending_popup()">Print</button>
        </div>`;

        let d = new frappe.ui.Dialog({
            title: "Item Details",
            fields: [{ fieldtype: "HTML", fieldname: "html" }]
        });

        d.fields_dict.html.$wrapper.html(html);
        d.show();
    }
};

window.print_pending_popup = function () {

    let content = document.getElementById("pending-popup").innerHTML;
    let w = window.open("", "", "width=1000,height=800");

    w.document.write(`
        <html>
        <head>
            <title>Fill Ratio</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid black; padding: 6px; text-align:center; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);

    w.document.close();
    w.print();
};
