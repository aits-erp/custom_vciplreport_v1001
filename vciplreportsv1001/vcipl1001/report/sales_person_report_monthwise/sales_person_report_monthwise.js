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
            fieldname: "custom_territory",
            label: __("Territory"),
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
        },
        {
            fieldname: "detailed_view",
            label: __("Detailed View"),
            fieldtype: "Check",
            default: 0,
            hidden: 1
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        if (!data) return default_formatter(value, row, column, data);
        
        value = default_formatter(value, row, column, data);
        
        // Make customer names clickable (Level 2 rows)
        if (column.fieldname == "customer_name" && data.level == "2" && data.customer_name && data.customer_name !== "TOTAL") {
            let customer = encodeURIComponent(data.customer_name);
            let sales_person = encodeURIComponent(data.sales_person || '');
            let month = frappe.query_report.get_filter_value('month');
            let year = frappe.query_report.get_filter_value('year');
            
            value = `<a style="color: #007bff; cursor: pointer; text-decoration: underline; font-weight: 500;" 
                onclick="frappe.query_reports['Sales Person Report Monthwise'].show_customer_details('${customer}', '${sales_person}', ${month}, ${year})">
                ${value} 🔍
            </a>`;
        }
        
        // Make invoice amounts clickable
        if (column.fieldname == "invoice_amount" && data.level == "2" && data.invoice_amount > 0) {
            let customer = encodeURIComponent(data.customer_name);
            let sales_person = encodeURIComponent(data.sales_person || '');
            let month = frappe.query_report.get_filter_value('month');
            let year = frappe.query_report.get_filter_value('year');
            
            value = `<a style="color: #28a745; cursor: pointer; text-decoration: underline;" 
                onclick="frappe.query_reports['Sales Person Report Monthwise'].show_invoice_breakdown('${customer}', '${sales_person}', ${month}, ${year})">
                ${value}
            </a>`;
        }
        
        // Color coding for achievement percentage
        if (column.fieldname == "achieved_pct" && data.achieved_pct !== undefined) {
            let pct = flt(data.achieved_pct);
            if (pct >= 100) {
                value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
            } else if (pct >= 75) {
                value = `<span style="color: #ffc107; font-weight: bold;">${value}</span>`;
            } else if (pct < 50 && pct > 0) {
                value = `<span style="color: #dc3545; font-weight: bold;">${value}</span>`;
            }
        }
        
        // Style for section headers
        if (data.level == "1") {
            value = `<span style="font-weight: bold; font-size: 1.1em; background-color: #f0f0f0; padding: 5px; display: block;">${value}</span>`;
        }
        
        // Style for total rows
        if (data.is_total_row) {
            value = `<span style="font-weight: bold; background-color: #f8f9fa;">${value}</span>`;
        }
        
        return value;
    },

    tree_view: function(data) {
        return data && data.indent !== undefined;
    },

    show_customer_details: function(customer, sales_person, month, year) {
        frappe.call({
            method: "your_app.your_app.report.sales_person_report_monthwise.sales_person_report_monthwise.get_customer_details",
            args: {
                customer: decodeURIComponent(customer),
                sales_person: decodeURIComponent(sales_person),
                month: month,
                year: year
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    show_customer_details_modal(r.message, decodeURIComponent(customer));
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

    show_invoice_breakdown: function(customer, sales_person, month, year) {
        frappe.call({
            method: "your_app.your_app.report.sales_person_report_monthwise.sales_person_report_monthwise.get_invoice_breakdown",
            args: {
                customer: decodeURIComponent(customer),
                sales_person: decodeURIComponent(sales_person),
                month: month,
                year: year
            },
            callback: function(r) {
                if (r.message && r.message.invoices && r.message.invoices.length > 0) {
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

    onload: function(report) {
        report.page.add_inner_button(__("Export to Excel"), function() {
            export_report("Excel");
        });
        
        report.page.add_inner_button(__("Export to PDF"), function() {
            export_report("PDF");
        });
        
        report.page.add_inner_button(__("Summary View"), function() {
            frappe.query_report.set_filter_value("detailed_view", 0);
            frappe.query_report.refresh();
        });
        
        report.page.add_inner_button(__("Detailed View"), function() {
            frappe.query_report.set_filter_value("detailed_view", 1);
            frappe.query_report.refresh();
        });
    }
};

function get_year_options() {
    let current_year = new Date().getFullYear();
    let years = [];
    for (let i = current_year - 5; i <= current_year + 2; i++) {
        years.push(i.toString());
    }
    return years;
}

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

function show_customer_details_modal(data, customer_name) {
    let total_qty = 0;
    let total_amount = 0;
    
    let rows = data.map(row => {
        total_qty += flt(row.qty);
        total_amount += flt(row.amount);
        return `
            <tr>
                <td>
                    <a href="/app/sales-invoice/${row.invoice_no}" target="_blank" style="color: #007bff;">
                        ${row.invoice_no}
                    </a>
                </td>
                <td>${row.posting_date}</td>
                <td>${row.item_name || row.item_code || ''}</td>
                <td style="text-align: right;">${format_number(row.qty)}</td>
                <td style="text-align: right;">${format_currency(row.amount)}</td>
            </tr>
        `;
    }).join('');
    
    let html = `
        <div style="max-height: 500px; overflow-y: auto; padding: 10px;">
            <h4 style="margin-bottom: 15px; color: #2c3e50; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                <i class="fa fa-user"></i> Customer: ${customer_name}
            </h4>
            <table class="table table-bordered table-hover">
                <thead style="background-color: #f8f9fa;">
                    <tr>
                        <th>Invoice No</th>
                        <th>Date</th>
                        <th>Item</th>
                        <th style="text-align: right;">Qty</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
                <tfoot style="background-color: #e9ecef; font-weight: bold;">
                    <tr>
                        <td colspan="3" style="text-align: right;">TOTAL:</td>
                        <td style="text-align: right;">${format_number(total_qty)}</td>
                        <td style="text-align: right;">${format_currency(total_amount)}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;
    
    frappe.msgprint({
        title: __("Customer Invoice Details"),
        message: html,
        wide: true
    });
}

function show_invoice_breakdown_modal(data, customer_name) {
    let rows = data.invoices.map(inv => {
        return `
            <tr>
                <td>
                    <a href="/app/sales-invoice/${inv.name}" target="_blank" style="color: #007bff;">
                        ${inv.name}
                    </a>
                </td>
                <td>${inv.posting_date}</td>
                <td style="text-align: right;">${format_number(inv.total_qty)}</td>
                <td style="text-align: right;">${format_currency(inv.total_amount)}</td>
            </tr>
        `;
    }).join('');
    
    let html = `
        <div style="max-height: 500px; overflow-y: auto; padding: 10px;">
            <h4 style="margin-bottom: 15px; color: #2c3e50; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                <i class="fa fa-file-invoice"></i> Invoice Breakdown - ${customer_name}
            </h4>
            <table class="table table-bordered">
                <thead style="background-color: #f8f9fa;">
                    <tr>
                        <th>Invoice No</th>
                        <th>Date</th>
                        <th style="text-align: right;">Total Qty</th>
                        <th style="text-align: right;">Total Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
                <tfoot style="background-color: #e9ecef; font-weight: bold;">
                    <tr>
                        <td colspan="3" style="text-align: right;">GRAND TOTAL:</td>
                        <td style="text-align: right;">${format_currency(data.grand_total)}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;
    
    frappe.msgprint({
        title: __("Invoice Summary"),
        message: html,
        wide: true
    });
}

function format_number(num) {
    if (!num) return '0';
    return new Intl.NumberFormat('en-IN', { 
        maximumFractionDigits: 2,
        minimumFractionDigits: 0
    }).format(num);
}

function format_currency(amt) {
    if (!amt) return '₹ 0.00';
    return new Intl.NumberFormat('en-IN', { 
        style: 'currency', 
        currency: 'INR',
        maximumFractionDigits: 2
    }).format(amt);
}

function flt(value) {
    return parseFloat(value) || 0;
}
