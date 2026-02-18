frappe.query_reports["Sales Person Report Monthwise"] = {
    filters: [
        {
            fieldname: "view_type",
            label: __("Select View"),
            fieldtype: "Select",
            options: [
                "CATEGORY WISE (Customer/Head)",
                "DISTRIBUTOR + TSO WISE",
                "HEAD WISE SUMMARY",
                "TSO WISE CATEGORY"
            ],
            default: "CATEGORY WISE (Customer/Head)",
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_end(),
            reqd: 1
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { value: 1, label: __("January") },
                { value: 2, label: __("February") },
                { value: 3, label: __("March") },
                { value: 4, label: __("April") },
                { value: 5, label: __("May") },
                { value: 6, label: __("June") },
                { value: 7, label: __("July") },
                { value: 8, label: __("August") },
                { value: 9, label: __("September") },
                { value: 10, label: __("October") },
                { value: 11, label: __("November") },
                { value: 12, label: __("December") }
            ],
            default: new Date().getMonth() + 1
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "sales_person",
            label: __("TSO Name"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "territory",
            label: __("Territory"),
            fieldtype: "Link",
            options: "Territory"
        }
    ],

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Make all values clickable for drill down
        if (data.customer_name && !data.is_total) {
            value = `<a style="color:#1674E0;cursor:pointer;text-decoration:underline"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_details("${data.customer_name}", "${data.sales_person || ''}", 
                "${data.month || ''}", ${JSON.stringify(data)})'>
                ${value}
            </a>`;
        }
        
        // Color coding for achieved %
        if (column.fieldname === "achieved_pct" && data.achieved_pct) {
            if (data.achieved_pct >= 100) value = `<span style="color:green;font-weight:bold">${value}</span>`;
            else if (data.achieved_pct >= 75) value = `<span style="color:orange;font-weight:bold">${value}</span>`;
            else if (data.achieved_pct < 50) value = `<span style="color:red;font-weight:bold">${value}</span>`;
        }
        
        return value;
    },

    show_details(customer, sales_person, month, data) {
        let html = `
        <div id="details-popup">
            <h4>Customer: ${customer}</h4>
            <h5>TSO: ${sales_person || 'All'}</h5>
            <table class="table table-bordered">
                <tr>
                    <th>Month</th>
                    <th>Sales Amount</th>
                    <th>Target</th>
                    <th>Achieved %</th>
                </tr>
        `;
        
        // Get monthly breakdown
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: customer,
                    docstatus: 1
                },
                fields: ["name", "posting_date", "base_net_total", "month(posting_date) as month_num"],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message) {
                    let monthly_data = {};
                    r.message.forEach(inv => {
                        let m = inv.month_num;
                        if (!monthly_data[m]) monthly_data[m] = 0;
                        monthly_data[m] += inv.base_net_total;
                    });
                    
                    for(let m=1; m<=12; m++) {
                        let amount = monthly_data[m] || 0;
                        html += `
                            <tr>
                                <td>${get_month_name(m)}</td>
                                <td style="text-align:right">${format_currency(amount)}</td>
                                <td style="text-align:right">0</td>
                                <td style="text-align:right">0%</td>
                            </tr>
                        `;
                    }
                    
                    html += `</table>
                        <button class="btn btn-primary" onclick="print_details()">Print</button>
                    </div>`;
                    
                    frappe.msgprint({
                        title: "Monthly Breakdown",
                        message: html,
                        wide: true
                    });
                }
            }
        });
    }
};

// Helper functions
function get_month_name(num) {
    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months[num-1];
}

function format_currency(amt) {
    return '₹ ' + (amt || 0).toLocaleString('en-IN', {maximumFractionDigits:2});
}

window.print_details = function() {
    let content = document.getElementById("details-popup").innerHTML;
    let w = window.open("", "", "width=900,height=700");
    w.document.write(`
        <html><head><title>Details</title>
        <style>body{font-family:Arial;padding:20px} table{border-collapse:collapse;width:100%}
        table,th,td{border:1px solid black;padding:6px}</style>
        </head><body>${content}</body></html>
    `);
    w.document.close();
    w.print();
};
