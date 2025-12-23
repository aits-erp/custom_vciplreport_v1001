frappe.query_reports["Distributors Report"] = {

    filters: [
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group",
            default: "Distributor"
        },
        {
            fieldname: "rsm",
            label: "RSM",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "asm",
            label: "ASM",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "tso",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person"
        }
    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "customer" && data.customer_code) {
            return `<a href="/app/customer/${data.customer_code}"
                target="_blank"
                style="font-weight:bold;color:#1674E0">
                ${value}
            </a>`;
        }

        if (column.fieldname === "total_outstanding" && data.outstanding_drill) {
            return this.make_link(value, data.outstanding_drill, "Outstanding Invoices");
        }

        if (column.fieldname === "total_overdue" && data.overdue_drill) {
            return this.make_link(value, data.overdue_drill, "Overdue Invoices");
        }

        if (column.fieldname === "avg_overdue_days" && data.avg_overdue_drill) {
            return this.make_link(value, data.avg_overdue_drill, "Invoices – Average Overdue Days");
        }

        if (column.fieldname === "avg_payment_days" && data.avg_payment_drill) {
            return this.make_link(value, data.avg_payment_drill, "Invoices – Average Payment Days");
        }

        return value;
    },

    make_link(value, data, title) {
        return `<a style="font-weight:bold;cursor:pointer;color:#1674E0"
            onclick='frappe.query_reports["Distributors Report"]
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
                       target="_blank"
                       style="font-weight:bold">
                        ${r.invoice}
                    </a>
                </td>
                <td>${r.posting_date}</td>
                <td>${r.due_date || r.payment_date || "-"}</td>
                <td>${r.amount ? format_currency(r.amount) : "-"}</td>
                <td>${r.days || r.overdue_days || "-"}</td>
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
