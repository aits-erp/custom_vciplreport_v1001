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

    // registry that holds drill-down payloads so we don't embed raw JSON in the DOM
    _drill_store: {}, 
    _drill_seq: 0,

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
            const raw = data[drill_field];

            if (raw) {
                let rows = [];
                try {
                    rows = typeof raw === "string" ? JSON.parse(raw) : raw;
                } catch (e) {
                    rows = [];
                }

                // only make it a link if there's actually something to show
                if (rows && rows.length) {
                    const me = frappe.query_reports["Distributors Report"];
                    const key = "d" + (me._drill_seq++);
                    me._drill_store[key] = { rows: rows, title: title };

                    return `<a style="font-weight:bold;cursor:pointer;color:#1674E0"
                               onclick='frappe.query_reports["Distributors Report"].show_popup_by_key("${key}")'>${value}</a>`;
                }
            }
        }

        return value;
    },

    show_popup_by_key(key) {
        const entry = this._drill_store[key];
        if (!entry) {
            frappe.msgprint(__("No data available"));
            return;
        }
        this.show_popup(entry.rows, entry.title);
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