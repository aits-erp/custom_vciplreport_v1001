frappe.query_reports["Monthwise Sales Report"] = {
    filters: [
        {
            fieldname: "customer_group",
            label: __("Customer Group"),
            fieldtype: "Link",
            options: "Customer Group"
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: (function () {
                let years = [];
                let current_year = new Date().getFullYear();

                for (let y = current_year; y >= 2020; y--) {
                    years.push(y.toString());
                }

                return years;
            })(),
            reqd: 0
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                "",
                "April","May","June",
                "July","August","September",
                "October","November","December",
                "January","February","March"
            ]
        }
    ],

    onload: function(report) {

        let today = new Date();
        let year = today.getFullYear();
        let month = today.getMonth() + 1;

        // Financial year logic
        if (month <= 3) {
            year = year - 1;
        }

        report.set_filter_value("year", year.toString());
        report.set_filter_value("month", "");

        report.refresh();
    },

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (
            column.fieldtype === "Currency" &&
            data &&
            data[column.fieldname + "_drill"] &&
            value > 0 &&
            !data.is_total_row
        ) {

            try {

                let drill_data = JSON.parse(data[column.fieldname + "_drill"]);

                if (drill_data.length > 0) {

                    return `<a style="font-weight:bold;color:#1674E0;cursor:pointer;text-decoration:underline;"
                        onclick='frappe.query_reports["Monthwise Sales Report"]
                        .show_drill_down(${JSON.stringify(drill_data)}, "${column.label}", "${data.customer_name}")'>
                        ${value}
                    </a>`;
                }

            } catch(e) {
                return value;
            }

        } else if (data && data.is_total_row) {

            return `<span style="font-weight:bold;">${value}</span>`;
        }

        return value;
    },

    show_drill_down(invoices, month, customer) {

        if (!invoices || invoices.length === 0) {
            frappe.msgprint(__("No Sales Invoices found"));
            return;
        }

        let total_amount = invoices.reduce((sum, inv) => sum + inv.amount, 0);

        let html = `
        <div style="max-height:500px;overflow:auto">

        <h4 style="margin-bottom:15px;border-bottom:2px solid #1674E0;padding-bottom:10px;">
        ${customer} - ${month}
        <span style="float:right;color:#1674E0;">
        Total: ${format_currency(total_amount)}
        </span>
        </h4>

        <table class="table table-bordered">

        <thead>
        <tr>
        <th>Sales Invoice</th>
        <th>Date</th>
        <th style="text-align:right;">Amount</th>
        </tr>
        </thead>

        <tbody>
        `;

        invoices.forEach(inv => {

            html += `
            <tr>

            <td>
            <a href="/app/sales-invoice/${inv.invoice}" target="_blank">
            ${inv.invoice}
            </a>
            </td>

            <td>${frappe.datetime.str_to_user(inv.date)}</td>

            <td style="text-align:right">
            ${format_currency(inv.amount)}
            </td>

            </tr>
            `;
        });

        html += `
        </tbody>

        <tfoot>
        <tr>
        <td colspan="2" style="text-align:right"><b>Total</b></td>
        <td style="text-align:right"><b>${format_currency(total_amount)}</b></td>
        </tr>
        </tfoot>

        </table>
        </div>
        `;

        frappe.msgprint({
            title: __("Invoice Details"),
            message: html,
            wide: true
        });

    }

};