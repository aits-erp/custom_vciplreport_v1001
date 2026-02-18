// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person Report Monthwise"] = {
    filters: [
        // Year Filter
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: get_year_options(),
            default: new Date().getFullYear().toString(),
            reqd: 1
        },
        
        // Month Filter
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { "value": 1, "label": __("January") },
                { "value": 2, "label": __("February") },
                { "value": 3, "label": __("March") },
                { "value": 4, "label": __("April") },
                { "value": 5, "label": __("May") },
                { "value": 6, "label": __("June") },
                { "value": 7, "label": __("July") },
                { "value": 8, "label": __("August") },
                { "value": 9, "label": __("September") },
                { "value": 10, "label": __("October") },
                { "value": 11, "label": __("November") },
                { "value": 12, "label": __("December") }
            ],
            default: new Date().getMonth() + 1,
            reqd: 1
        },
        
        // Head Sales Person Filter
        {
            fieldname: "parent_sales_person",
            label: __("Head Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        
        // Sales Person Filter
        {
            fieldname: "sales_person",
            label: __("Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        
        // Region Filter
        {
            fieldname: "custom_region",
            label: __("Region"),
            fieldtype: "Data"
        },
        
        // Location Filter
        {
            fieldname: "custom_location",
            label: __("Location"),
            fieldtype: "Data"
        },
        
        // Territory Filter
        {
            fieldname: "custom_territory",
            label: __("Territory"),
            fieldtype: "Data"
        },
        
        // Customer Filter
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        
        // Include Targets Toggle
        {
            fieldname: "include_targets",
            label: __("Include Targets"),
            fieldtype: "Check",
            default: 1
        },
        
        // Compare with Previous Year
        {
            fieldname: "compare_previous_year",
            label: __("Compare with Previous Year"),
            fieldtype: "Check",
            default: 0
        }
    ],

    // Formatter for better visualization
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Color coding for achievement percentage
        if (column.fieldname == "achieved_pct" && data.achieved_pct !== undefined) {
            if (data.achieved_pct >= 100) {
                value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
            } else if (data.achieved_pct >= 75) {
                value = `<span style="color: #ffc107; font-weight: bold;">${value}</span>`;
            } else if (data.achieved_pct < 50 && data.achieved_pct > 0) {
                value = `<span style="color: #dc3545; font-weight: bold;">${value}</span>`;
            }
        }
        
        // Highlight total row
        if (data.is_total_row) {
            value = `<span style="font-weight: bold; background-color: #f0f0f0;">${value}</span>`;
        }
        
        // Make customer names clickable for drill-down
        if (column.fieldname == "customer_name" && data.customer_name && data.customer_name !== "TOTAL") {
            value = `<a style="color: #007bff; cursor: pointer; text-decoration: underline;" 
                onclick="frappe.query_reports['Sales Person Report Monthwise'].open_customer_details('${data.customer_name}', '${data.sales_person}')">
                ${value}
            </a>`;
        }
        
        return value;
    },

    // Drill-down to customer details
    open_customer_details: function(customer_name, sales_person) {
        frappe.call({
            method: "your_app.your_app.report.sales_person_report_monthwise.sales_person_report_monthwise.get_customer_details",
            args: {
                customer: customer_name,
                sales_person: sales_person,
                month: frappe.query_report.get_filter_value("month"),
                year: frappe.query_report.get_filter_value("year")
            },
            callback: function(r) {
                if (r.message) {
                    show_customer_details_modal(r.message, customer_name);
                }
            }
        });
    },

    // Tree view toggle
    tree_view: function(data) {
        // Enable tree view for hierarchical data
        return data && data.indent !== undefined;
    },

    // On load event
    onload: function(report) {
        // Add export buttons
        report.page.add_inner_button(__("Export to Excel"), function() {
            frappe.query_reports["Sales Person Report Monthwise"].export_report(report, "Excel");
        });
        
        report.page.add_inner_button(__("Export to PDF"), function() {
            frappe.query_reports["Sales Person Report Monthwise"].export_report(report, "PDF");
        });
        
        // Add view toggle buttons
        report.page.add_inner_button(__("Summary View"), function() {
            frappe.query_report.set_filter_value("detailed_view", 0);
        });
        
        report.page.add_inner_button(__("Detailed View"), function() {
            frappe.query_report.set_filter_value("detailed_view", 1);
        });
        
        // Add hidden filter for view type
        report.add_filter({
            fieldname: "detailed_view",
            label: __("Detailed View"),
            fieldtype: "Check",
            hidden: 1,
            default: 0
        });
    },

    // Export function
    export_report: function(report, format) {
        var filters = report.get_values();
        
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
};

// Helper function to generate year options
function get_year_options() {
    let current_year = new Date().getFullYear();
    let years = [];
    for (let i = current_year - 5; i <= current_year + 1; i++) {
        years.push(i.toString());
    }
    return years;
}

// Helper function to show customer details modal
function show_customer_details_modal(data, customer_name) {
    let html = `
        <div style="max-height: 500px; overflow-y: auto;">
            <h4>Customer: ${customer_name}</h4>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Invoice No</th>
                        <th>Date</th>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    let total_amount = 0;
    
    data.forEach(row => {
        total_amount += row.amount;
        html += `
            <tr>
                <td><a href="/app/sales-invoice/${row.invoice_no}" target="_blank">${row.invoice_no}</a></td>
                <td>${row.posting_date}</td>
                <td>${row.item_name}</td>
                <td style="text-align: right;">${row.qty}</td>
                <td style="text-align: right;">${format_currency(row.amount)}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
                <tfoot>
                    <tr style="font-weight: bold;">
                        <td colspan="4" style="text-align: right;">Total:</td>
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

// Helper function to format currency
function format_currency(amount) {
    return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD' 
    }).format(amount);
}
