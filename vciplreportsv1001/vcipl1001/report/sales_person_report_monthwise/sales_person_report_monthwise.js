frappe.query_reports["Sales Person Report Monthwise"] = {

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "achieved" && data.ach_drill) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_popup(${data.ach_drill})'>
                ${value}
            </a>`;
        }

        return value;
    },

    show_popup(rows) {

        if (!rows || rows.length === 0) {
            frappe.msgprint("No invoices found");
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
            title: "Achieved Invoice Details",
            message: html,
            wide: true
        });
    }
};
