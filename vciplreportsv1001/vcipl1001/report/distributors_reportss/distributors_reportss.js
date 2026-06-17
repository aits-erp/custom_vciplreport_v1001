frappe.query_reports["Distributors Report"] = {

    filters: [
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group",
            default: "Debtors Distributors"
        }
    ],

    // column fieldname -> [drill field on the row, popup title]
    drill_map: {
        total_outstanding: ["outstanding_drill", "Outstanding Invoices"],
        total_overdue:     ["overdue_drill", "Overdue Invoices"],
        avg_overdue_days:  ["avg_overdue_drill", "Invoices – Average Overdue Days"],
        avg_payment_days:  ["avg_payment_drill", "Invoices – Average Payment Days"],
        aging_0_15:        ["aging_0_15_drill", "0-15 Days"],
        aging_16_30:       ["aging_16_30_drill", "16-30 Days"],
        aging_31_45:       ["aging_31_45_drill", "31+ Days"]
    },

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        // Distributor name -> customer link
        if (column.fieldname === "customer" && data.customer_code) {
            return `<a href="/app/customer/${data.customer_code}"
                       target="_blank"
                       style="font-weight:bold;color:#1674E0">${value}</a>`;
        }

        // Clickable drill-down columns
        const drill = this.drill_map[column.fieldname];
        if (drill) {
            const [drill_field, title] = drill;
            if (data[drill_field]) {
                const payload = encodeURIComponent(data[drill_field]);
                const enc_title = encodeURIComponent(title);
                return `<a class="dist-drill"
                           data-payload="${payload}"
                           data-title="${enc_title}"
                           style="font-weight:bold;cursor:pointer;color:#1674E0">${value}</a>`;
            }
        }

        return value;
    },

    onload(report) {
        // Inline onclick is stripped by Frappe's HTML sanitizer, so we bind
        // the click via event delegation on a stable parent instead.
        $(report.page.wrapper)
            .off("click.distDrill")
            .on("click.distDrill", "a.dist-drill", function () {
                const payload = $(this).attr("data-payload");
                const title = decodeURIComponent($(this).attr("data-title"));

                let rows = [];
                try {
                    rows = JSON.parse(decodeURIComponent(payload));
                } catch (e) {
                    frappe.msgprint(__("Could not read drill-down data"));
                    return;
                }

                frappe.query_reports["Distributors Report"].show_popup(rows, title);
            });
    },

    show_popup(rows, title) {

        if (title === "Invoices – Average Overdue Days") {
            rows = rows.filter(r => flt(r.amount) > 0);
        }

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
                    <th>Due / Payment Date</th>
                    <th>Amount</th>
                    <th>Days</th>
                </tr>
            </thead><tbody>`;

        rows.forEach(r => {
            html += `
            <tr>
                <td>
                    <a href="/app/sales-invoice/${r.invoice}"
                       target="_blank" style="font-weight:bold">${r.invoice}</a>
                </td>
                <td>${r.posting_date}</td>
                <td>${r.due_date || r.payment_date || "-"}</td>
                <td>${r.amount ? format_currency(r.amount) : "-"}</td>
                <td>${r.days || r.overdue_days || "-"}</td>
            </tr>`;
        });

        html += `</tbody></table></div>`;

        frappe.msgprint({ title: title, message: html, wide: true });
    }
};