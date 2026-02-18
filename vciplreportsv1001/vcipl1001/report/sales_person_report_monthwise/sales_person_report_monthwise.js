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
            fieldname: "parent_sales_person",
            label: __("Head Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "sales_person",
            label: __("Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "custom_region",
            label: __("Region"),
            fieldtype: "Data"
        },
        {
            fieldname: "custom_location",
            label: __("Location"),
            fieldtype: "Data"
        },
        {
            fieldname: "custom_territory_name",
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
        
        // Make customer names clickable (Level 2 rows) - Like your reference code
        if (column.fieldname === "customer_name" && data.level === "2" && data.customer_name && data.customer_name !== "TOTAL") {
            let customer = encodeURIComponent(data.customer_name);
            let sales_person = encodeURIComponent(data.sales_person || '');
            let month = frappe.query_report.get_filter_value('month');
            let year = frappe.query_report.get_filter_value('year');
            
            // Using the same pattern as your reference code
            value = `<a style="color:#1674E0;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_customer_details("${customer}", "${sales_person}", ${month}, ${year})'>
                ${value} 🔍
            </a>`;
        }
        
        // Make invoice amounts clickable - Like your reference code
        if (column.fieldname === "invoice_amount" && data.level === "2" && data.invoice_amount > 0) {
            let customer = encodeURIComponent(data.customer_name);
            let sales_person = encodeURIComponent(data.sales_person || '');
            let month = frappe.query_report.get_filter_value('month');
            let year = frappe.query_report.get_filter_value('year');
            
            value = `<a style="color:#28a745;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_invoice_breakdown("${customer}", "${sales_person}", ${month}, ${year})'>
                ${value}
            </a>`;
        }
        
        // Color coding for achievement percentage - Like your reference code
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
        if (data.level === "1") {
            value = `<span style="font-weight:bold;font-size:1.1em;background-color:#f0f0f0;padding:5px;display:block">${value}</span>`;
        }
        
        // Style for total rows
        if (data.is_total_row) {
            value = `<span style="font-weight:bold;background-color:#f8f9fa">${value}</span>`;
        }
        
        return value;
    },

    // Tree view for hierarchical data
    tree_view: true,

    // Customer details popup - Like your show_popup function
    show_customer_details(customer, sales_person, month, year) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: decodeURIComponent(customer),
                    docstatus: 1,
                    posting_date: ["between", [
                        frappe.datetime.month_start(`${year}-${month}-01`),
                        frappe.datetime.month_end(`${year}-${month}-01`)
                    ]]
                },
                fields: ["name", "posting_date"],
                limit_page_length: 100
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    // Get invoice names
                    let invoice_names = r.message.map(inv => inv.name);
                    
                    // Get items for these invoices
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Sales Invoice Item",
                            filters: {
                                parent: ["in", invoice_names]
                            },
                            fields: ["parent as invoice_no", "item_code", "item_name", "qty", "base_net_amount as amount"],
                            limit_page_length: 500
                        },
                        callback: function(r2) {
                            if (r2.message) {
                                show_customer_details_modal(r2.message, decodeURIComponent(customer));
                            }
                        }
                    });
                } else {
                    frappe.msgprint({
                        title: __("No Details Found"),
                        message: __("No invoice details found for {0} in this period", [decodeURIComponent(customer)]),
                        indicator: "orange"
                    });
                }
            }
        });
    },

    // Invoice breakdown popup
    show_invoice_breakdown(customer, sales_person, month, year) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: decodeURIComponent(customer),
                    docstatus: 1,
                    posting_date: ["between", [
                        frappe.datetime.month_start(`${year}-${month}-01`),
                        frappe.datetime.month_end(`${year}-${month}-01`)
                    ]]
                },
                fields: ["name", "posting_date", "base_net_total as total_amount"],
                limit_page_length: 100
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    show_invoice_breakdown_modal(r.message, decodeURIComponent(customer));
                } else {
                    frappe.msgprint({
                        title: __("No Details Found"),
                        message: __("No invoices found for {0} in this period", [decodeURIComponent(customer)]),
                        indicator: "orange"
                    });
                }
            }
        });
    },

    // On load event
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
        method: "frappe.desk.query_report.export_query",
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

// Customer details modal - Following your reference code pattern
function show_customer_details_modal(data, customer_name) {
    let total_qty = 0;
    let total_amount = 0;
    
    let html = `
        <div id="customer-details-popup" style="max-height:450px;overflow:auto">
            <h4>Customer: ${customer_name}</h4>
            <table class="table table-bordered">
                <tr>
                    <th>Invoice No</th>
                    <th>Date</th>
                    <th>Item Name</th>
                    <th>Qty</th>
                    <th>Amount</th>
                </tr>
    `;
    
    data.forEach(row => {
        total_qty += row.qty || 0;
        total_amount += row.amount || 0;
        
        html += `
            <tr>
                <td><a href="/app/sales-invoice/${row.invoice_no}" target="_blank">${row.invoice_no}</a></td>
                <td>${row.posting_date || ''}</td>
                <td>${row.item_name || row.item_code || ''}</td>
                <td style="text-align:right">${format_number(row.qty)}</td>
                <td style="text-align:right">${format_currency(row.amount)}</td>
            </tr>
        `;
    });
    
    html += `
                <tr style="font-weight:bold;background-color:#f7f7f7">
                    <td colspan="3" style="text-align:right">TOTAL:</td>
                    <td style="text-align:right">${format_number(total_qty)}</td>
                    <td style="text-align:right">${format_currency(total_amount)}</td>
                </tr>
            </table>
        </div>
        <button class="btn btn-primary" onclick="print_customer_details()">Print</button>
    `;
    
    frappe.msgprint({
        title: __("Customer Invoice Details"),
        message: html,
        wide: true
    });
}

// Invoice breakdown modal - Following your reference code pattern
function show_invoice_breakdown_modal(data, customer_name) {
    let total_amount = 0;
    
    let html = `
        <div id="invoice-breakdown-popup" style="max-height:450px;overflow:auto">
            <h4>Invoice Summary - ${customer_name}</h4>
            <table class="table table-bordered">
                <tr>
                    <th>Invoice No</th>
                    <th>Date</th>
                    <th>Amount</th>
                </tr>
    `;
    
    data.forEach(inv => {
        total_amount += inv.total_amount || 0;
        
        html += `
            <tr>
                <td><a href="/app/sales-invoice/${inv.name}" target="_blank">${inv.name}</a></td>
                <td>${inv.posting_date}</td>
                <td style="text-align:right">${format_currency(inv.total_amount)}</td>
            </tr>
        `;
    });
    
    html += `
                <tr style="font-weight:bold;background-color:#f7f7f7">
                    <td colspan="2" style="text-align:right">GRAND TOTAL:</td>
                    <td style="text-align:right">${format_currency(total_amount)}</td>
                </tr>
            </table>
        </div>
        <button class="btn btn-primary" onclick="print_invoice_breakdown()">Print</button>
    `;
    
    frappe.msgprint({
        title: __("Invoice Summary"),
        message: html,
        wide: true
    });
}

// Print functions - Following your reference code pattern
window.print_customer_details = function() {
    let content = document.getElementById("customer-details-popup").innerHTML;
    
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

window.print_invoice_breakdown = function() {
    let content = document.getElementById("invoice-breakdown-popup").innerHTML;
    
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
    return num.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

function format_currency(amt) {
    if (!amt) return '₹ 0.00';
    return '₹ ' + amt.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}
