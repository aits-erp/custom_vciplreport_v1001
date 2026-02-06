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
        },
        {
            fieldname: "risk_filter",
            label: __("Risk Level"),
            fieldtype: "Select",
            options: ["", "HIGH", "Medium", "OK"]
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        // Risk coloring
        if (column.fieldname === "risk") {

            if (data.risk === "Critical") {
                value = `<span style="color:red;font-weight:bold">🔴 HIGH</span>`;
            }

            if (data.risk === "Warning") {
                value = `<span style="color:orange;font-weight:bold">🟠 Medium</span>`;
            }

            if (data.risk === "OK") {
                value = `<span style="color:green;font-weight:bold">🟢 OK</span>`;
            }
        }

        // Fill ratio coloring
        if (column.fieldname === "fill_ratio") {

            if (data.fill_ratio < 50) {
                value = `<span style="color:red;font-weight:bold">${data.fill_ratio}%</span>`;
            } else if (data.fill_ratio < 80) {
                value = `<span style="color:orange;font-weight:bold">${data.fill_ratio}%</span>`;
            } else {
                value = `<span style="color:green;font-weight:bold">${data.fill_ratio}%</span>`;
            }
        }

        // Popup link
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

        let html = `<h3>Fill Ratio Details</h3>
        <h4>Party: ${party}</h4>
        <h5>Order: ${order_id}</h5>
        <table class="table table-bordered">
        <thead>
        <tr>
            <th>Item</th><th>Ordered</th><th>Delivered</th>
            <th>Pending</th><th>Available</th>
            <th>Fill %</th><th>Date</th>
        </tr></thead><tbody>`;

        rows.forEach(r => {
            html += `<tr>
                <td>${r.item_name}</td>
                <td>${r.ordered_qty}</td>
                <td>${r.delivered_qty}</td>
                <td>${r.pending_qty}</td>
                <td>${r.available_qty}</td>
                <td>${r.ratio}%</td>
                <td>${r.delivery_date}</td>
            </tr>`;
        });

        html += `<tr style="font-weight:bold;background:#f3f3f3">
            <td>Total</td>
            <td>${totals.ordered}</td>
            <td>${totals.delivered}</td>
            <td>${totals.pending}</td>
            <td colspan="3"></td>
        </tr></tbody></table>`;

        let d = new frappe.ui.Dialog({
            title: "Item Details",
            fields: [{ fieldtype: "HTML", fieldname: "html" }]
        });

        d.fields_dict.html.$wrapper.html(html);
        d.show();
    }
};
