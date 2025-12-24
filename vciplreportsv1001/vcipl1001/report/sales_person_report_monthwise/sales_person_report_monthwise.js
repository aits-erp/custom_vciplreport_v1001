frappe.query_reports["Sales Person Report Monthwise"] = {

    // =====================
    // STATE
    // =====================
    show_achievement: false,

    // =====================
    // ONLOAD
    // =====================
    onload(report) {
        this.add_button(report);
    },

    // =====================
    // BUTTON
    // =====================
    add_button(report) {
        report.page.add_inner_button(
            __("Generate Achievement"),
            () => {
                this.show_achievement = !this.show_achievement;
                this.toggle_columns(report);
            }
        );
    },

    // =====================
    // TOGGLE COLUMNS
    // =====================
    toggle_columns(report) {

        const ach_fields = [
            "total_achieved",
            "jan_achieved",
            "feb_achieved"
        ];

        report.columns.forEach(col => {
            if (ach_fields.includes(col.fieldname)) {
                col.hidden = !this.show_achievement;
            }
        });

        report.refresh();
    },

    // =====================
    // FORMATTER (CLICK → POPUP)
    // =====================
    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        const drill_map = {
            "total_achieved": "total_ach_drill",
            "jan_achieved": "jan_ach_drill",
            "feb_achieved": "feb_ach_drill"
        };

        if (drill_map[column.fieldname] && data[drill_map[column.fieldname]]) {
            return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                onclick='frappe.query_reports["Distributors Report"]
                .show_popup(${data[drill_map[column.fieldname]]}, "${column.label}")'>
                ${value}
            </a>`;
        }

        return value;
    },

    // =====================
    // POPUP
    // =====================
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
