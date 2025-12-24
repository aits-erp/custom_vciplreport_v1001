frappe.query_reports["Sales Person Report Monthwise"] = {

    filters: [
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Int",
            default: new Date().getFullYear()
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname.endsWith("_ach") && data.ach_drill) {

            return `<a style="font-weight:bold;color:#1a73e8"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_popup(${data.ach_drill}, "${column.label}")'>
                ${value}
            </a>`;
        }

        return value;
    },

    show_popup(rows, title) {

        rows = JSON.parse(rows || "[]");

        if (!rows.length) {
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
            title: title,
            message: html,
            wide: true
        });
    }
};
