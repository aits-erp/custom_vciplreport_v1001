frappe.query_reports["Monthwise Sales Report"] = {

    filters: [
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ],
            default: moment().format("MMM"),
            reqd: 1
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "month_amount" && data.month_drill) {
            return this.make_link(value, data.month_drill, "Sales Invoices");
        }

        return value;
    },

    make_link(value, data, title) {
        return `<a style="font-weight:bold;cursor:pointer;color:#1674E0"
            onclick='frappe.query_reports["Monthwise Sales Report"]
            .show_popup(${data}, "${title}")'>
            ${value}
        </a>`;
    },

    show_popup(rows, title) {

        if (!rows || rows.length === 0) {
            frappe.msgprint(__("No data available"));
            return;
        }

        let html = `
        <div style="max-height:500px;overflow:auto">
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Invoice</th>
                    <th>Posting Date</th>
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
                <td>${r.posting_date}</td>
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
