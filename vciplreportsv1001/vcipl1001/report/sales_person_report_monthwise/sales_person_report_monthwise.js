frappe.query_reports["Sales Person Report Monthwise"] = {

    show_achievement: false,

    onload(report) {
        report.page.add_inner_button(
            __("Generate Achievement"),
            () => {
                this.show_achievement = !this.show_achievement;
                this.toggle_columns(report);
            }
        );
    },

    toggle_columns(report) {
        report.columns.forEach(col => {
            if (col.fieldname.endsWith("_achieved") || col.fieldname.endsWith("_pct")) {
                col.hidden = !this.show_achievement;
            }
        });
        report.refresh();
    },

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data) return value;

        if (column.fieldname.endsWith("_achieved") && data[column.fieldname.replace("_achieved", "_ach_drill")]) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Sales Person Target Report"]
                .show_popup(${data[column.fieldname.replace("_achieved", "_ach_drill")]},
                "${column.label}")'>${value}</a>`;
        }

        if (column.fieldname === "total_achieved" && data.total_ach_drill) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Sales Person Target Report"]
                .show_popup(${data.total_ach_drill}, "Total Achievement")'>${value}</a>`;
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
                <td><a href="/app/sales-invoice/${r.invoice}" target="_blank">${r.invoice}</a></td>
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
