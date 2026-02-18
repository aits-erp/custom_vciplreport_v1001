// Copyright (c) 2024, Your Company
// For license information, please see license.txt

frappe.query_reports["Sales Person Report Monthwise"] = {
    filters: [
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
        // Date Filters
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
        // Month Filter
        {
            fieldname: "month",
            label: __("Specific Month"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("All Months") },
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
            default: ""
        },
        // Sales Person Hierarchy Filters
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
        // Territory Filters
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
        // Customer Filters
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
        // Item Filters
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
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data"
        },
        // Additional Options
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
            fieldname: "show_zero_rows",
            label: __("Show Zero Value Rows"),
            fieldtype: "Check",
            default: 0
        }
    ],

    // ============= DYNAMIC COLUMN FORMATTER =============
    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Make EVERYTHING clickable based on column type
        
        // 1. Customer Names Clickable
        if (column.fieldname === "customer_name" || column.fieldname === "customer" || column.fieldname === "distributor") {
            let customer = data.customer_name || data.customer || data.distributor || value;
            if (customer && !customer.includes("TOTAL") && !customer.includes("<b>")) {
                value = `<a style="color:#1674E0;cursor:pointer;text-decoration:underline;font-weight:500"
                    onclick='frappe.query_reports["Sales Person Report Monthwise"]
                    .show_customer_popup("${customer}", "${data.tso_name || data.sales_person || ''}")'>
                    ${value} 🔍
                </a>`;
            }
        }
        
        // 2. TSO Names Clickable
        else if (column.fieldname === "tso_name" || column.fieldname === "sales_person") {
            let tso = data.tso_name || data.sales_person || value;
            if (tso && !tso.includes("TOTAL")) {
                value = `<a style="color:#28a745;cursor:pointer;text-decoration:underline;font-weight:500"
                    onclick='frappe.query_reports["Sales Person Report Monthwise"]
                    .show_tso_popup("${tso}", "${data.customer_name || data.customer || ''}")'>
                    ${value} 👤
                </a>`;
            }
        }
        
        // 3. Head Sales Person Clickable
        else if (column.fieldname === "head_sales_person") {
            let head = data.head_sales_person || value;
            if (head && !head.includes("TOTAL")) {
                value = `<a style="color:#6f42c1;cursor:pointer;text-decoration:underline;font-weight:500"
                    onclick='frappe.query_reports["Sales Person Report Monthwise"]
                    .show_head_popup("${head}")'>
                    ${value} 👑
                </a>`;
            }
        }
        
        // 4. Sales/Invoice Amount Clickable
        else if (column.fieldname === "sales" || column.fieldname === "invoice_amount" || 
                 column.fieldname === "amount" || column.fieldname.includes("amount")) {
            if (data[column.fieldname] > 0) {
                let customer = data.customer_name || data.customer || data.distributor || '';
                let tso = data.tso_name || data.sales_person || '';
                let item = data.item_group || data.category || '';
                
                value = `<a style="color:#dc3545;cursor:pointer;text-decoration:underline;font-weight:500"
                    onclick='frappe.query_reports["Sales Person Report Monthwise"]
                    .show_invoice_popup("${customer}", "${tso}", "${item}")'>
                    ${value} 💰
                </a>`;
            }
        }
        
        // 5. Target Amount Clickable
        else if (column.fieldname === "target" && data.target > 0) {
            value = `<a style="color:#fd7e14;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_target_popup("${data.customer_name || data.customer || ''}", 
                "${data.tso_name || data.sales_person || ''}")'>
                ${value} 🎯
            </a>`;
        }
        
        // 6. Item Groups Clickable
        else if (column.fieldname === "item_group" || column.fieldname === "custom_main_group" || 
                 column.fieldname === "custom_sub_group") {
            let group = data[column.fieldname] || value;
            if (group && !group.includes("TOTAL")) {
                value = `<a style="color:#20c997;cursor:pointer;text-decoration:underline;font-weight:500"
                    onclick='frappe.query_reports["Sales Person Report Monthwise"]
                    .show_item_popup("${group}", "${data.customer_name || ''}")'>
                    ${value} 📦
                </a>`;
            }
        }
        
        // 7. Month Name Clickable
        else if (column.fieldname === "month" && data.month && !data.month.includes("TOTAL")) {
            value = `<a style="color:#6c757d;cursor:pointer;text-decoration:underline;font-weight:500"
                onclick='frappe.query_reports["Sales Person Report Monthwise"]
                .show_month_popup("${data.month}", "${data.customer_name || ''}")'>
                ${value} 📅
            </a>`;
        }
        
        // Color coding for achievement percentage
        if (column.fieldname === "achieved_pct" && data.achieved_pct !== undefined) {
            let pct = parseFloat(data.achieved_pct);
            if (pct >= 100) {
                value = `<span style="color:#28a745;font-weight:bold">${value} ✅</span>`;
            } else if (pct >= 75) {
                value = `<span style="color:#ffc107;font-weight:bold">${value} ⚠️</span>`;
            } else if (pct > 0) {
                value = `<span style="color:#dc3545;font-weight:bold">${value} ❌</span>`;
            }
        }
        
        // Style for total rows
        if (data.is_total || (data.customer_name && data.customer_name.includes("TOTAL"))) {
            value = `<span style="font-weight:bold;background-color:#f0f0f0;padding:2px 5px">${value}</span>`;
        }
        
        return value;
    },

    // ============= POPUP FUNCTIONS =============
    
    // Customer Popup - Shows all invoices for customer
    show_customer_popup(customer, tso) {
        let filters = frappe.query_report.get_filter_values();
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    customer: customer,
                    docstatus: 1,
                    posting_date: ["between", [filters.from_date, filters.to_date]]
                },
                fields: ["name", "posting_date", "base_net_total"],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let html = build_invoice_table(r.message, customer, tso);
                    frappe.msgprint({
                        title: __("Customer Invoices"),
                        message: html,
                        wide: true
                    });
                } else {
                    frappe.msgprint({
                        title: __("No Data"),
                        message: __("No invoices found for {0}", [customer]),
                        indicator: "orange"
                    });
                }
            }
        });
    },
    
    // TSO Popup - Shows TSO performance
    show_tso_popup(tso, customer) {
        let filters = frappe.query_report.get_filter_values();
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice",
                filters: {
                    docstatus: 1,
                    posting_date: ["between", [filters.from_date, filters.to_date]]
                },
                fields: ["name", "customer", "base_net_total", "posting_date"],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message) {
                    let html = build_tso_table(r.message, tso);
                    frappe.msgprint({
                        title: __("TSO Performance"),
                        message: html,
                        wide: true
                    });
                }
            }
        });
    },
    
    // Head Popup
    show_head_popup(head) {
        frappe.msgprint({
            title: __("Head Sales Person"),
            message: `<div id="popup-content"><h4>👑 ${head}</h4><p>Loading details...</p></div>`,
            wide: true
        });
    },
    
    // Invoice Popup - Shows item details
    show_invoice_popup(customer, tso, item) {
        let filters = frappe.query_report.get_filter_values();
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Invoice Item",
                filters: {
                    docstatus: 1
                },
                fields: ["parent as invoice_no", "item_code", "item_name", "qty", "base_net_amount as amount"],
                limit_page_length: 200
            },
            callback: function(r) {
                if (r.message) {
                    let html = build_item_table(r.message, customer, tso);
                    frappe.msgprint({
                        title: __("Item Details"),
                        message: html,
                        wide: true
                    });
                }
            }
        });
    },
    
    // Target Popup
    show_target_popup(customer, tso) {
        frappe.msgprint({
            title: __("Target Details"),
            message: `<div id="popup-content"><h4>🎯 Target for ${customer}</h4><p>Loading...</p></div>`,
            wide: true
        });
    },
    
    // Item Popup
    show_item_popup(group, customer) {
        frappe.msgprint({
            title: __("Item Group Details"),
            message: `<div id="popup-content"><h4>📦 ${group}</h4><p>Customer: ${customer}</p></div>`,
            wide: true
        });
    },
    
    // Month Popup
    show_month_popup(month, customer) {
        frappe.msgprint({
            title: __("Monthly Details"),
            message: `<div id="popup-content"><h4>📅 ${month}</h4><p>Customer: ${customer}</p></div>`,
            wide: true
        });
    },

    // Tree view for hierarchical data
    tree_view: true,
    
    // On report load
    onload: function(report) {
        // Add export buttons
        report.page.add_inner_button(__("Export to Excel"), function() {
            export_report("Excel");
        });
        
        report.page.add_inner_button(__("Export to PDF"), function() {
            export_report("PDF");
        });
        
        report.page.add_inner_button(__("Print Report"), function() {
            window.print();
        });
        
        // Add CSS
        frappe.dom.set_style(`
            .report-column a { cursor: pointer; }
            .report-column a:hover { text-decoration: underline !important; }
            .popup-table { width: 100%; border-collapse: collapse; }
            .popup-table th { background-color: #f2f2f2; padding: 8px; }
            .popup-table td { padding: 6px; border: 1px solid #ddd; }
        `);
    }
};

// ============= HELPER FUNCTIONS =============

function build_invoice_table(invoices, customer, tso) {
    let total = 0;
    let rows = invoices.map(inv => {
        total += inv.base_net_total;
        return `
            <tr>
                <td><a href="/app/sales-invoice/${inv.name}" target="_blank">${inv.name}</a></td>
                <td>${inv.posting_date}</td>
                <td style="text-align:right">${format_currency(inv.base_net_total)}</td>
            </tr>
        `;
    }).join('');
    
    return `
        <div id="popup-content">
            <h4 style="color:#1674E0">🔍 Customer: ${customer}</h4>
            <h5>TSO: ${tso || 'All'}</h5>
            <div style="max-height:400px;overflow:auto">
                <table class="table table-bordered table-hover">
                    <thead>
                        <tr><th>Invoice No</th><th>Date</th><th style="text-align:right">Amount</th></tr>
                    </thead>
                    <tbody>${rows}</tbody>
                    <tfoot style="font-weight:bold;background:#f0f0f0">
                        <tr><td colspan="2" style="text-align:right">TOTAL:</td>
                        <td style="text-align:right">${format_currency(total)}</td></tr>
                    </tfoot>
                </table>
            </div>
            <button class="btn btn-primary" onclick="window.print_popup()">🖨️ Print</button>
        </div>
    `;
}

function build_tso_table(invoices, tso) {
    return `
        <div id="popup-content">
            <h4 style="color:#28a745">👤 TSO: ${tso}</h4>
            <p>Total Invoices: ${invoices.length}</p>
            <button class="btn btn-primary" onclick="window.print_popup()">🖨️ Print</button>
        </div>
    `;
}

function build_item_table(items, customer, tso) {
    let total_qty = 0, total_amt = 0;
    let rows = items.slice(0, 50).map(item => {
        total_qty += item.qty || 0;
        total_amt += item.amount || 0;
        return `
            <tr>
                <td><a href="/app/sales-invoice/${item.invoice_no}" target="_blank">${item.invoice_no}</a></td>
                <td>${item.item_code || ''}</td>
                <td>${item.item_name || ''}</td>
                <td style="text-align:right">${format_number(item.qty)}</td>
                <td style="text-align:right">${format_currency(item.amount)}</td>
            </tr>
        `;
    }).join('');
    
    return `
        <div id="popup-content">
            <h4 style="color:#dc3545">💰 Invoice Items</h4>
            <h5>Customer: ${customer} | TSO: ${tso}</h5>
            <div style="max-height:400px;overflow:auto">
                <table class="table table-bordered">
                    <thead>
                        <tr><th>Invoice</th><th>Item Code</th><th>Item Name</th>
                        <th style="text-align:right">Qty</th><th style="text-align:right">Amount</th></tr>
                    </thead>
                    <tbody>${rows}</tbody>
                    <tfoot style="font-weight:bold;background:#f0f0f0">
                        <tr><td colspan="3" style="text-align:right">TOTAL:</td>
                        <td style="text-align:right">${format_number(total_qty)}</td>
                        <td style="text-align:right">${format_currency(total_amt)}</td></tr>
                    </tfoot>
                </table>
            </div>
            <button class="btn btn-primary" onclick="window.print_popup()">🖨️ Print</button>
        </div>
    `;
}

function format_currency(amt) {
    return '₹ ' + (amt || 0).toLocaleString('en-IN', {maximumFractionDigits: 0});
}

function format_number(num) {
    return (num || 0).toLocaleString('en-IN', {maximumFractionDigits: 0});
}

function export_report(format) {
    let filters = frappe.query_report.get_filter_values();
    frappe.call({
        method: "frappe.desk.query_report.export",
        args: {
            report_name: "Sales Person Report Monthwise",
            report_type: "Custom Report",
            filters: filters,
            file_format_type: format,
            title: `Sales_Report_${filters.view_type}_${filters.from_date}_${filters.to_date}`
        },
        callback: function(r) {
            if (r.message) window.open(r.message);
        }
    });
}

window.print_popup = function() {
    let content = document.getElementById("popup-content")?.innerHTML;
    if (!content) return;
    
    let w = window.open("", "", "width=1000,height=700");
    w.document.write(`
        <html><head><title>Sales Report</title>
        <style>body{font-family:Arial;padding:30px} table{border-collapse:collapse;width:100%}
        th,td{border:1px solid #999;padding:8px} th{background:#f2f2f2}</style>
        </head><body>${content}</body></html>
    `);
    w.document.close();
    w.print();
};
