frappe.query_reports["Customer & Supplier Fill Ratio"] = {

    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        { fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
        { fieldname: "to_date", label: __("To Date"), fieldtype: "Date" }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "fill_ratio") {

            if (data.fill_ratio < 50)
                value = `<span style="color:red;font-weight:bold">${data.fill_ratio}%</span>`;
            else if (data.fill_ratio < 80)
                value = `<span style="color:orange;font-weight:bold">${data.fill_ratio}%</span>`;
            else
                value = `<span style="color:green;font-weight:bold">${data.fill_ratio}%</span>`;
        }

        if (column.fieldname === "risk") {

            if (data.risk === "Critical")
                value = `<span style="color:red;font-weight:bold">🔴 Critical</span>`;
            else if (data.risk === "Warning")
                value = `<span style="color:orange;font-weight:bold">🟠 Warning</span>`;
            else
                value = `<span style="color:green;font-weight:bold">🟢 OK</span>`;
        }

        if (column.fieldname === "order_count" && data.order_popup) {

            let safe = encodeURIComponent(data.order_popup);

            value = `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='show_orders("${safe}", "${data.party}")'>
                ${data.order_count}
            </a>`;
        }

        return value;
    }
};


// ================= PRINT =================

window.print_section = function(id) {

    let content = document.getElementById(id).innerHTML;

    let w = window.open("", "", "width=1000,height=800");

    w.document.write(`
        <html>
        <head>
            <title>Print</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid black; padding: 6px; text-align:center; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);

    w.document.close();
    w.print();
};


// ================= LEVEL 2 =================

window.show_orders = function(encoded, party) {

    let rows = JSON.parse(decodeURIComponent(encoded));

    let tot_qty = 0, tot_del = 0;

    let html = `<div id="print_orders">
    <h3>Pending Orders — ${party}</h3>
    <table class="table table-bordered">
    <thead>
        <tr>
            <th>SO No</th>
            <th>Date</th>
            <th>Pending Delivery</th>
            <th>Ordered</th>
            <th>Delivered</th>
            <th>Fill %</th>
        </tr>
    </thead><tbody>`;

    rows.forEach(r => {

        tot_qty += r.qty;
        tot_del += r.delivered;

        let safe = encodeURIComponent(r.pending_popup);

        html += `<tr>
            <td><b>${r.so_no}</b></td>
            <td>${r.so_date}</td>
            <td><a style="color:red;font-weight:bold;cursor:pointer"
                onclick='show_items("${safe}")'>View Pending</a></td>
            <td>${r.qty}</td>
            <td>${r.delivered}</td>
            <td>${r.fill_ratio}%</td>
        </tr>`;
    });

    let total_ratio = tot_qty ? ((tot_del / tot_qty) * 100).toFixed(2) : 0;

    html += `<tr style="font-weight:bold;background:#eee">
        <td colspan="3">Grand Total</td>
        <td>${tot_qty}</td>
        <td>${tot_del}</td>
        <td>${total_ratio}%</td>
    </tr></tbody></table></div>`;

    let d = new frappe.ui.Dialog({
        title: "Order Details",
        size: "extra-large",
        fields: [{ fieldtype: "HTML", fieldname: "html" }]
    });

    d.fields_dict.html.$wrapper.html(`
        ${html}
        <button class="btn btn-primary"
            onclick="print_section('print_orders')">Print</button>
    `);

    d.show();
};


// ================= LEVEL 3 =================

window.show_items = function(encoded) {

    let rows = JSON.parse(decodeURIComponent(encoded));

    let tot_qty = 0, tot_del = 0, tot_pen = 0;

    let html = `<div id="print_items">
    <h3>Pending Items</h3>
    <table class="table table-bordered">
    <thead>
        <tr>
            <th>Item</th>
            <th>Ordered</th>
            <th>Delivered</th>
            <th>Pending</th>
            <th>Fill %</th>
        </tr>
    </thead><tbody>`;

    rows.forEach(r => {

        let ratio = r.qty ? ((r.delivered / r.qty) * 100).toFixed(2) : 0;

        tot_qty += r.qty;
        tot_del += r.delivered;
        tot_pen += r.pending;

        html += `<tr>
            <td>${r.item}</td>
            <td>${r.qty}</td>
            <td>${r.delivered}</td>
            <td style="color:red;font-weight:bold">${r.pending}</td>
            <td>${ratio}%</td>
        </tr>`;
    });

    let total_ratio = tot_qty ? ((tot_del / tot_qty) * 100).toFixed(2) : 0;

    html += `<tr style="font-weight:bold;background:#eee">
        <td>Grand Total</td>
        <td>${tot_qty}</td>
        <td>${tot_del}</td>
        <td>${tot_pen}</td>
        <td>${total_ratio}%</td>
    </tr></tbody></table></div>`;

    let d = new frappe.ui.Dialog({
        title: "Pending Items",
        size: "large",
        fields: [{ fieldtype: "HTML", fieldname: "html" }]
    });

    d.fields_dict.html.$wrapper.html(`
        ${html}
        <button class="btn btn-primary"
            onclick="print_section('print_items')">Print</button>
    `);

    d.show();
};
