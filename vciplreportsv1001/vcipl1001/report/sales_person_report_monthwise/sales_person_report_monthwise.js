// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person Report Monthwise"] = {
    filters: [
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: get_year_options(),
            default: new Date().getFullYear().toString(),
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
            default: new Date().getMonth() + 1,
            reqd: 1
        },
        {
            fieldname: "territory_name",
            label: __("Territory Name"),
            fieldtype: "Data"
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "include_targets",
            label: __("Include Targets"),
            fieldtype: "Check",
            default: 1
        },
        {
            fieldname: "compare_previous_year",
            label: __("Compare with Previous Year"),
            fieldtype: "Check",
            default: 0
        }
    ],

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Make customer names clickable - EXACTLY like your reference code
        if (column.fieldname === "customer_name" && data.customer_name && !data.customer_name.includes("TOTAL") && !data.customer_name.includes("SALES PERSON PERFORMANCE")) {
            let customer = encodeURIComponent(data.customer_name);
            let month = frappe.query_report.get_filter_value('month');
            let year = frappe.query_report.get_filter_value('year');
            
            value = `<a style="font-weight:bold;color:#1674E0;cursor:pointer;text-decoration:underline"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_customer_popup("${customer}", ${month}, ${year})'>
                ${value} 🔍
            </a>`;
        }
        
        // Make invoice amounts clickable - EXACTLY like your reference code
        if (column.fieldname === "invoice_amount" && data.invoice_amount > 0 && !data.customer_name.includes("TOTAL")) {
            let customer = encodeURIComponent(data.customer_name);
            let month = frappe.query_report.get_filter_value('month');
            let year = frappe.query_report.get_filter_value('year');
            
            value = `<a style="font-weight:bold;color:#28a745;cursor:pointer;text-decoration:underline"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_invoice_popup("${customer}", ${month}, ${year})'>
                ${value}
            </a>`;
        }
        
        // Color coding for achievement percentage
        if (column.fieldname === "achieved_pct" && data.achieved_pct !== undefined) {
            if (data.achieved_pct >= 100) {
                value = `<span style="color:#28a745;font-weight:bold">${value}</span>`;
            } else if (data.achieved_pct >= 75) {
                value = `<span style="color:#ffc107;font-weight:bold">${value}</span>`;
            } else if (data.achieved_pct < 50 && data.achieved_pct > 0) {
                value = `<span style="color:#dc3545;font-weight:bold">${value}</span>`;
            }
        }
        
        // Style for section headers
        if (data.customer_name === "SALES PERSON PERFORMANCE") {
            value = `<span style="font-weight:bold;font-size:1.1em;background-color:#f0f0f0;padding:5px;display:block">${value}</span>`;
        }
        
        // Style for total rows
        if (data.customer_name && data.customer_name.includes("TOTAL")) {
            value = `<span style="font-weight:bold;background-color:#f8f9fa">${value}</span>`;
        }
        
        return value;
    },

    // Customer popup function - EXACTLY like your reference code's show_popup
    show_customer_popup(customer, month, year) {
        let decoded_customer = decodeURIComponent(customer);
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: decoded_customer,
                    docstatus: 1,
                    posting_date: ["between", [
                        frappe.datetime.month_start(`${year}-${month}-01`),
                        frappe.datetime.month_end(`${year}-${month}-01`)
                    ]]
                },
                fields: ["name", "posting_date"],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let invoice_names = r.message.map(inv => inv.name);
                    
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Sales Invoice Item",
                            filters: {
                                parent: ["in", invoice_names]
                            },
                            fields: ["parent as invoice_no", "item_name", "qty", "base_net_amount as amount"],
                            limit_page_length: 1000
                        },
                        callback: function(r2) {
                            if (r2.message) {
                                let rows = r2.message;
                                show_customer_popup_modal(rows, decoded_customer);
                            }
                        }
                    });
                } else {
                    frappe.msgprint({
                        title: __("No Details Found"),
                        message: __("No invoices found for {0}", [decoded_customer]),
                        indicator: "orange"
                    });
                }
            }
        });
    },

    // Invoice popup function - EXACTLY like your reference code's show_popup
    show_invoice_popup(customer, month, year) {
        let decoded_customer = decodeURIComponent(customer);
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: decoded_customer,
                    docstatus: 1,
                    posting_date: ["between", [
                        frappe.datetime.month_start(`${year}-${month}-01`),
                        frappe.datetime.month_end(`${year}-${month}-01`)
                    ]]
                },
                fields: ["name", "posting_date", "base_net_total as amount"],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    show_invoice_popup_modal(r.message, decoded_customer);
                } else {
                    frappe.msgprint({
                        title: __("No Details Found"),
                        message: __("No invoices found for {0}", [decoded_customer]),
                        indicator: "orange"
                    });
                }
            }
        });
    },

    onload: function(report) {
        report.page.add_inner_button(__("Export to Excel"), function() {
            export_report("Excel");
        });
        
        report.page.add_inner_button(__("Export to PDF"), function() {
            export_report("PDF");
        });
    }
};

// Helper function to generate year options
function get_year_options() {
    let current_year = new Date().getFullYear();
    let years = [];
    for (let i = current_year - 5; i <= current_year + 2; i++) {
        years.push(i.toString());
    }
    return years;
}

// Export function
function export_report(format) {
    var filters = frappe.query_report.get_filter_values();
    
    frappe.call({
        method: "frappe.desk.query_report.export",
        args: {
            report_name: "Sales Person Report Monthwise",
            report_type: "Custom Report",
            filters: filters,
            file_format_type: format,
            title: `Sales_Person_Report_${filters.month}_${filters.year}`
        },
        callback: function(r) {
            if (r.message) {
                window.open(r.message);
            }
        }
    });
}

// Customer popup modal - EXACTLY like your reference code's HTML structure
function show_customer_popup_modal(rows, customer_name) {
    let total_qty = 0;
    let total_amount = 0;
    
    let html = `
    <div id="customer-popup">
        <h4>Customer: ${customer_name}</h4>
        <div style="max-height:450px;overflow:auto">
            <table class="table table-bordered">
                <tr>
                    <th>Invoice No</th>
                    <th>Item Name</th>
                    <th>Qty</th>
                    <th>Amount</th>
                </tr>
    `;
    
    rows.forEach(r => {
        total_qty += r.qty || 0;
        total_amount += r.amount || 0;
        
        html += `
            <tr>
                <td><a href="/app/sales-invoice/${r.invoice_no}" target="_blank">${r.invoice_no}</a></td>
                <td>${r.item_name}</td>
                <td style="text-align:right">${format_number(r.qty)}</td>
                <td style="text-align:right">${format_currency(r.amount)}</td>
            </tr>
        `;
    });
    
    html += `
                <tr style="font-weight:bold;background:#f7f7f7">
                    <td colspan="2" style="text-align:right">TOTAL:</td>
                    <td style="text-align:right">${format_number(total_qty)}</td>
                    <td style="text-align:right">${format_currency(total_amount)}</td>
                </tr>
            </table>
        </div>
        <button class="btn btn-primary" onclick="print_customer_popup()">Print</button>
    </div>`;
    
    frappe.msgprint({
        title: __("Customer Invoice Details"),
        message: html,
        wide: true
    });
}

// Invoice popup modal - EXACTLY like your reference code's HTML structure
function show_invoice_popup_modal(rows, customer_name) {
    let total_amount = 0;
    
    let html = `
    <div id="invoice-popup">
        <h4>Invoices - ${customer_name}</h4>
        <div style="max-height:450px;overflow:auto">
            <table class="table table-bordered">
                <tr>
                    <th>Invoice No</th>
                    <th>Date</th>
                    <th>Amount</th>
                </tr>
    `;
    
    rows.forEach(r => {
        total_amount += r.amount || 0;
        
        html += `
            <tr>
                <td><a href="/app/sales-invoice/${r.name}" target="_blank">${r.name}</a></td>
                <td>${r.posting_date}</td>
                <td style="text-align:right">${format_currency(r.amount)}</td>
            </tr>
        `;
    });
    
    html += `
                <tr style="font-weight:bold;background:#f7f7f7">
                    <td colspan="2" style="text-align:right">TOTAL:</td>
                    <td style="text-align:right">${format_currency(total_amount)}</td>
                </tr>
            </table>
        </div>
        <button class="btn btn-primary" onclick="print_invoice_popup()">Print</button>
    </div>`;
    
    frappe.msgprint({
        title: __("Invoice Summary"),
        message: html,
        wide: true
    });
}

// Print functions - EXACTLY like your reference code
window.print_customer_popup = function() {
    let content = document.getElementById("customer-popup").innerHTML;
    
    let w = window.open("", "", "width=900,height=700");
    w.document.write(`
        <html>
        <head>
            <title>Customer Invoice Details</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid black; padding: 6px; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);
    
    w.document.close();
    w.print();
};

window.print_invoice_popup = function() {
    let content = document.getElementById("invoice-popup").innerHTML;
    
    let w = window.open("", "", "width=900,height=700");
    w.document.write(`
        <html>
        <head>
            <title>Invoice Summary</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid black; padding: 6px; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);
    
    w.document.close();
    w.print();
};

// Helper functions
function format_number(num) {
    if (!num) return '0';
    return num.toLocaleString('en-IN');
}

function format_currency(amt) {
    if (!amt) return '₹ 0.00';
    return '₹ ' + amt.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}
