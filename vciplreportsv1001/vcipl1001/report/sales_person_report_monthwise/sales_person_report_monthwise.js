// Copyright (c) 2024, Your Company
// For license information, please see license.txt

frappe.query_reports["Sales Person Report Monthwise"] = {
    filters: [
        // ============= VIEW TYPE FILTER =============
        {
            fieldname: "view_type",
            label: __("Select Report View"),
            fieldtype: "Select",
            options: [
                "CATEGORY WISE (Customer/Head)",
                "DISTRIBUTOR + TSO WISE", 
                "HEAD WISE SUMMARY",
                "TSO WISE CATEGORY"
            ],
            default: "TSO WISE CATEGORY",
            reqd: 1
        },

        // ============= DATE FILTERS =============
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

        // ============= MONTH FILTER =============
        {
            fieldname: "month",
            label: __("Select Month"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("All Months") },
                { value: "1", label: __("January") },
                { value: "2", label: __("February") },
                { value: "3", label: __("March") },
                { value: "4", label: __("April") },
                { value: "5", label: __("May") },
                { value: "6", label: __("June") },
                { value: "7", label: __("July") },
                { value: "8", label: __("August") },
                { value: "9", label: __("September") },
                { value: "10", label: __("October") },
                { value: "11", label: __("November") },
                { value: "12", label: __("December") }
            ],
            default: ""
        },

        // ============= SALES PERSON HIERARCHY FILTERS =============
        {
            fieldname: "parent_sales_person",
            label: __("Head Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "sales_person",
            label: __("TSO/Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ============= TERRITORY FILTERS =============
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

        // ============= CUSTOMER FILTERS =============
        {
            fieldname: "customer",
            label: __("Customer/Distributor"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "customer_group",
            label: __("Customer Group"),
            fieldtype: "Link",
            options: "Customer Group"
        },

        // ============= ITEM FILTERS =============
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
        },
        {
            fieldname: "custom_main_group",
            label: __("Main Group"),
            fieldtype: "Data"
        },
        {
            fieldname: "custom_sub_group",
            label: __("Sub Group"),
            fieldtype: "Data"
        },

        // ============= OPTIONS =============
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

    // ============= FORMATTER =============
    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Make customer names clickable
        if ((column.fieldname === "customer_name" || column.fieldname === "customer" || column.fieldname === "distributor") 
            && data.customer_name && !data.customer_name.includes("TOTAL")) {
            
            let customer = encodeURIComponent(data.customer_name);
            
            value = `<a style="color:#1674E0;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_customer_popup("${customer}")'>
                ${value} 🔍
            </a>`;
        }
        
        // Make TSO names clickable
        if ((column.fieldname === "tso_name" || column.fieldname === "sales_person") 
            && data.tso_name && !data.tso_name.includes("TOTAL")) {
            
            let tso = encodeURIComponent(data.tso_name);
            
            value = `<a style="color:#28a745;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_tso_popup("${tso}")'>
                ${value} 👤
            </a>`;
        }
        
        // Make sales amounts clickable
        if ((column.fieldname === "sales" || column.fieldname === "invoice_amount") && data.sales > 0) {
            let customer = encodeURIComponent(data.customer_name || '');
            let amount = data.sales;
            
            value = `<a style="color:#dc3545;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_amount_popup("${customer}", ${amount})'>
                ${value} 💰
            </a>`;
        }
        
        // Color coding for achievement percentage
        if (column.fieldname === "achieved_pct" && data.achieved_pct !== undefined) {
            let pct = parseFloat(data.achieved_pct);
            if (pct >= 100) {
                value = `<span style="color:green;font-weight:bold">${value} ✅</span>`;
            } else if (pct >= 75) {
                value = `<span style="color:orange;font-weight:bold">${value} ⚠️</span>`;
            } else if (pct > 0) {
                value = `<span style="color:red;font-weight:bold">${value} ❌</span>`;
            }
        }
        
        return value;
    },

    // ============= POPUP FUNCTIONS =============
    
    show_customer_popup(customer) {
        let customer_name = decodeURIComponent(customer);
        let filters = frappe.query_report.get_filter_values();
        
        // Show loading
        let loading = frappe.msgprint({
            title: __("Loading..."),
            message: `<div style="text-align:center;padding:20px">
                <i class="fa fa-spinner fa-spin" style="font-size:24px"></i>
                <p>Fetching data for ${customer_name}...</p>
            </div>`
        });
        
        // Get all invoices for this customer
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: customer_name,
                    docstatus: 1,
                    posting_date: ["between", [filters.from_date, filters.to_date]]
                },
                fields: ["name", "posting_date", "base_net_total", "MONTH(posting_date) as month_num"],
                limit_page_length: 5000
            },
            callback: function(r) {
                if (loading) loading.hide();
                
                let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                
                // Initialize monthly data
                let monthly_data = {};
                months.forEach(m => { monthly_data[m] = 0; });
                
                // Fill with actual data
                if (r.message && r.message.length > 0) {
                    r.message.forEach(inv => {
                        let month_name = months[inv.month_num - 1];
                        monthly_data[month_name] += inv.base_net_total;
                    });
                }
                
                // Build table
                let html = `
                <div id="customer-popup">
                    <h4 style="color:#1674E0;margin-bottom:15px">📋 Customer: ${customer_name}</h4>
                    <h5 style="margin-bottom:20px">Period: ${filters.from_date} to ${filters.to_date}</h5>
                    <div style="max-height:450px;overflow:auto">
                        <table class="table table-bordered">
                            <thead style="background:#f0f0f0">
                                <tr>
                                    <th>Month</th>
                                    <th style="text-align:right">Sales Amount</th>
                                    <th style="text-align:right">Target</th>
                                    <th style="text-align:right">Achieved %</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                let total_sales = 0;
                months.forEach(month => {
                    let amount = monthly_data[month] || 0;
                    total_sales += amount;
                    
                    html += `
                        <tr>
                            <td><b>${month}</b></td>
                            <td style="text-align:right">${format_currency(amount)}</td>
                            <td style="text-align:right">0</td>
                            <td style="text-align:right">0%</td>
                        </tr>
                    `;
                });
                
                html += `
                            </tbody>
                            <tfoot style="background:#e0e0e0;font-weight:bold">
                                <tr>
                                    <td>TOTAL</td>
                                    <td style="text-align:right">${format_currency(total_sales)}</td>
                                    <td style="text-align:right">0</td>
                                    <td style="text-align:right">-</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                    <div style="margin-top:15px;text-align:center">
                        <button class="btn btn-primary" onclick="window.print_popup()">
                            <i class="fa fa-print"></i> Print
                        </button>
                    </div>
                </div>`;
                
                frappe.msgprint({
                    title: __("Monthly Breakdown"),
                    message: html,
                    wide: true
                });
            }
        });
    },
    
    show_tso_popup(tso) {
        let tso_name = decodeURIComponent(tso);
        let filters = frappe.query_report.get_filter_values();
        
        frappe.msgprint({
            title: __("TSO Details"),
            message: `
                <div id="tso-popup">
                    <h4 style="color:#28a745">👤 TSO: ${tso_name}</h4>
                    <p>Loading performance data...</p>
                    <button class="btn btn-primary" onclick="window.print_popup()">Print</button>
                </div>
            `,
            wide: true
        });
    },
    
    show_amount_popup(customer, amount) {
        let customer_name = decodeURIComponent(customer);
        
        frappe.msgprint({
            title: __("Amount Details"),
            message: `
                <div id="amount-popup">
                    <h4 style="color:#dc3545">💰 Amount: ${format_currency(amount)}</h4>
                    <p><b>Customer:</b> ${customer_name}</p>
                    <p>Click on customer name to see monthly breakdown</p>
                    <button class="btn btn-primary" onclick="window.print_popup()">Print</button>
                </div>
            `,
            wide: true
        });
    },

    // ============= ONLOAD =============
    onload: function(report) {
        // Add CSS
        frappe.dom.set_style(`
            .report-column a { cursor: pointer; }
            .report-column a:hover { text-decoration: underline !important; }
            #customer-popup table { width: 100%; border-collapse: collapse; }
            #customer-popup th { background-color: #f2f2f2; padding: 10px; }
            #customer-popup td { padding: 8px; border: 1px solid #ddd; }
        `);
        
        // Add export buttons
        report.page.add_inner_button(__("Export to Excel"), function() {
            let filters = report.get_values();
            frappe.call({
                method: "frappe.desk.query_report.export",
                args: {
                    report_name: "Sales Person Report Monthwise",
                    report_type: "Custom Report",
                    filters: filters,
                    file_format_type: "Excel",
                    title: `Sales_Report_${filters.view_type}`
                },
                callback: function(r) {
                    if (r.message) window.open(r.message);
                }
            });
        });
        
        report.page.add_inner_button(__("Print Report"), function() {
            window.print();
        });
    }
};

// ============= HELPER FUNCTIONS =============

function format_currency(amt) {
    if (!amt || amt === 0) return '₹ 0';
    return '₹ ' + Number(amt).toLocaleString('en-IN', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 0
    });
}

// Global print function
window.print_popup = function() {
    let content = document.getElementById("customer-popup")?.innerHTML || 
                  document.getElementById("tso-popup")?.innerHTML ||
                  document.getElementById("amount-popup")?.innerHTML;
    
    if (!content) {
        frappe.msgprint(__("Nothing to print"));
        return;
    }
    
    let w = window.open("", "", "width=1000,height=700");
    w.document.write(`
        <html>
        <head>
            <title>Sales Report Details</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 30px; }
                h4 { color: #333; margin-bottom: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #999; padding: 10px; }
                th { background-color: #f2f2f2; font-weight: bold; }
                tfoot { background-color: #e6e6e6; font-weight: bold; }
                .btn { display: none; }
            </style>
        </head>
        <body>
            ${content}
        </body>
        </html>
    `);
    w.document.close();
    w.print();
};
