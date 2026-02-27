// total_sales_report.js
// eslint-disable-next-line
frappe.query_reports["TOTAL SALES REPORT"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "width": "100px"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "100px"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "width": "100px"
        },
        {
            "fieldname": "region",
            "label": __("Region"),
            "fieldtype": "Select",
            "options": [
                "",
                "North",
                "South",
                "East",
                "West",
                "Central"
            ],
            "width": "100px"
        },
        {
            "fieldname": "show_ytd",
            "label": __("Show YTD Totals"),
            "fieldtype": "Check",
            "default": 1,
            "width": "100px"
        },
        {
            "fieldname": "show_annual",
            "label": __("Show Annual Totals"),
            "fieldtype": "Check",
            "default": 1,
            "width": "100px"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Format based on column type
        if (column.fieldname.includes("_pct")) {
            // Percentage columns with color coding
            let pct_value = data[column.fieldname];
            
            if (pct_value === 0 || pct_value === null || pct_value === undefined) {
                value = `<span style="color: #6c757d;">0%</span>`;
            } else if (pct_value >= 100) {
                value = `<span style="background-color: #d4edda; color: #155724; padding: 3px 10px; border-radius: 15px; font-weight: bold;">${pct_value.toFixed(1)}%</span>`;
            } else if (pct_value >= 80) {
                value = `<span style="background-color: #fff3cd; color: #856404; padding: 3px 10px; border-radius: 15px; font-weight: bold;">${pct_value.toFixed(1)}%</span>`;
            } else if (pct_value > 0) {
                value = `<span style="background-color: #f8d7da; color: #721c24; padding: 3px 10px; border-radius: 15px; font-weight: bold;">${pct_value.toFixed(1)}%</span>`;
            }
        }
        
        // Format currency columns
        if (column.fieldname.includes("_sales") || column.fieldname.includes("_target") || column.fieldname.includes("_ly")) {
            if (value && value !== "0.00") {
                let num_value = parseFloat(value.replace(/[^0-9.-]+/g, ""));
                if (num_value > 1000000) {
                    value = `<span style="font-weight: 500;">${value}</span>`;
                }
            }
        }
        
        // Highlight total rows
        if (data.month === "TOTAL YTD" || data.month === "TOTAL ANNUAL") {
            if (column.fieldname === "month") {
                value = `<span style="font-weight: bold; color: #1e446d;">${value}</span>`;
            } else {
                value = `<span style="font-weight: 600;">${value}</span>`;
            }
        }
        
        return value;
    },

    "onload": function(report) {
        // Add custom buttons
        report.page.add_inner_button(__("Export to Excel"), function() {
            export_to_excel(report);
        });
        
        report.page.add_inner_button(__("View Summary"), function() {
            show_summary_dialog(report);
        });
        
        // Add refresh button
        report.page.add_inner_button(__("Refresh Data"), function() {
            report.refresh();
        });
    },

    "after_datatable_render": function(report) {
        // Add custom styling after table renders
        setTimeout(function() {
            add_custom_styling();
        }, 100);
    },

    "refresh": function(report) {
        // Any custom logic on refresh
        console.log("Total Sales Report Refreshed");
    }
};

// Helper function to export to Excel
function export_to_excel(report) {
    let filters = report.get_values();
    let data = report.data;
    
    if (!data || data.length === 0) {
        frappe.msgprint(__("No data to export"));
        return;
    }
    
    // Create workbook structure
    let wb_data = [];
    
    // Add headers
    let headers = [];
    report.columns.forEach(col => {
        headers.push(col.label);
    });
    wb_data.push(headers);
    
    // Add data rows
    data.forEach(row => {
        let row_data = [];
        report.columns.forEach(col => {
            row_data.push(row[col.fieldname] || 0);
        });
        wb_data.push(row_data);
    });
    
    // Export as CSV
    let csv_content = wb_data.map(row => 
        row.map(cell => {
            if (typeof cell === 'string' && cell.includes(',')) {
                return `"${cell}"`;
            }
            return cell;
        }).join(',')
    ).join('\n');
    
    let blob = new Blob([csv_content], { type: 'text/csv' });
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = `total_sales_report_${frappe.datetime.nowdate()}.csv`;
    a.click();
    
    frappe.show_alert({
        message: __("Report exported successfully"),
        indicator: "green"
    });
}

// Show summary dialog with key metrics
function show_summary_dialog(report) {
    let data = report.data;
    if (!data || data.length < 3) {
        frappe.msgprint(__("Insufficient data for summary"));
        return;
    }
    
    // Get YTD and Annual rows
    let ytd_row = data.find(row => row.month === "TOTAL YTD");
    let annual_row = data.find(row => row.month === "TOTAL ANNUAL");
    
    if (!ytd_row || !annual_row) {
        frappe.msgprint(__("YTD or Annual data not available"));
        return;
    }
    
    // Calculate overall metrics
    let distributors = ['agarwal', 'agrawal', 'bhagat', 'hindustan'];
    let total_ytd_sales = 0;
    let total_ytd_target = 0;
    let total_annual_target = 0;
    let total_annual_ly = 0;
    
    distributors.forEach(dist => {
        total_ytd_sales += ytd_row[`${dist}_sales`] || 0;
        total_ytd_target += ytd_row[`${dist}_target`] || 0;
        total_annual_target += annual_row[`${dist}_target`] || 0;
        total_annual_ly += annual_row[`${dist}_ly`] || 0;
    });
    
    // Create dialog
    let dialog = new frappe.ui.Dialog({
        title: __("Sales Summary"),
        size: "large",
        fields: [
            {
                fieldtype: "HTML",
                fieldname: "summary_html",
                options: `
                    <div style="padding: 15px;">
                        <h4 style="margin-bottom: 20px; color: #1e446d;">Key Performance Indicators</h4>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                                <div style="font-size: 14px; color: #6c757d; margin-bottom: 10px;">YTD Achievement</div>
                                <div style="font-size: 28px; font-weight: bold; color: #28a745;">
                                    ${((total_ytd_sales / total_ytd_target) * 100).toFixed(1)}%
                                </div>
                                <div style="font-size: 13px; color: #6c757d; margin-top: 10px;">
                                    ₹${format_number(total_ytd_sales)} / ₹${format_number(total_ytd_target)}
                                </div>
                            </div>
                            
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                                <div style="font-size: 14px; color: #6c757d; margin-bottom: 10px;">Annual Target vs LY</div>
                                <div style="font-size: 28px; font-weight: bold; color: #007bff;">
                                    ${((total_annual_target / total_annual_ly) * 100).toFixed(1)}%
                                </div>
                                <div style="font-size: 13px; color: #6c757d; margin-top: 10px;">
                                    Target: ₹${format_number(total_annual_target)}
                                </div>
                            </div>
                            
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                                <div style="font-size: 14px; color: #6c757d; margin-bottom: 10px;">Growth (YTD vs LY)</div>
                                <div style="font-size: 28px; font-weight: bold; color: #17a2b8;">
                                    ${((total_ytd_sales - total_annual_ly) / total_annual_ly * 100).toFixed(1)}%
                                </div>
                                <div style="font-size: 13px; color: #6c757d; margin-top: 10px;">
                                    Current: ₹${format_number(total_ytd_sales)}
                                </div>
                            </div>
                        </div>
                        
                        <h5 style="margin: 20px 0 15px; color: #495057;">Distributor Performance</h5>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #e9ecef;">
                                    <th style="padding: 12px; text-align: left;">Distributor</th>
                                    <th style="padding: 12px; text-align: right;">YTD Sales</th>
                                    <th style="padding: 12px; text-align: right;">YTD Target</th>
                                    <th style="padding: 12px; text-align: right;">Achieved %</th>
                                    <th style="padding: 12px; text-align: right;">Annual Target</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${generate_distributor_rows(ytd_row, annual_row, distributors)}
                            </tbody>
                        </table>
                    </div>
                `
            }
        ],
        primary_action_label: __("Close"),
        primary_action: function() {
            dialog.hide();
        }
    });
    
    dialog.show();
}

// Helper function to format numbers
function format_number(num) {
    if (!num) return "0";
    if (num >= 10000000) {
        return (num / 10000000).toFixed(2) + " Cr";
    } else if (num >= 100000) {
        return (num / 100000).toFixed(2) + " Lac";
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + " K";
    }
    return num.toString();
}

// Generate distributor rows for summary
function generate_distributor_rows(ytd_row, annual_row, distributors) {
    let dist_names = {
        'agarwal': 'AGARWAL DISTRIBUTOR',
        'agrawal': 'AGRAWAL METAL STORES',
        'bhagat': 'BHAGAT TRADING COMPANY',
        'hindustan': 'HINDUSTAN TRADERS'
    };
    
    let rows = '';
    distributors.forEach(dist => {
        let sales = ytd_row[`${dist}_sales`] || 0;
        let target = ytd_row[`${dist}_target`] || 0;
        let annual_target = annual_row[`${dist}_target`] || 0;
        let pct = target ? (sales / target * 100).toFixed(1) : 0;
        let color = pct >= 100 ? '#28a745' : (pct >= 80 ? '#ffc107' : '#dc3545');
        
        rows += `
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 10px; text-align: left;">${dist_names[dist]}</td>
                <td style="padding: 10px; text-align: right;">₹${format_number(sales)}</td>
                <td style="padding: 10px; text-align: right;">₹${format_number(target)}</td>
                <td style="padding: 10px; text-align: right;">
                    <span style="color: white; background: ${color}; padding: 3px 10px; border-radius: 12px; font-weight: bold;">
                        ${pct}%
                    </span>
                </td>
                <td style="padding: 10px; text-align: right;">₹${format_number(annual_target)}</td>
            </tr>
        `;
    });
    
    return rows;
}

// Add custom CSS styling
function add_custom_styling() {
    let style = document.createElement('style');
    style.innerHTML = `
        .dt-row.dt-row-header {
            background-color: #f8f9fa !important;
            font-weight: 600;
        }
        
        .dt-cell {
            border-right: 1px solid #dee2e6;
        }
        
        .dt-cell:last-child {
            border-right: none;
        }
        
        /* Style for total rows */
        tr[data-rowname*="TOTAL"] {
            background-color: #e9ecef !important;
            font-weight: 600;
            border-top: 2px solid #1e446d;
            border-bottom: 2px solid #1e446d;
        }
        
        /* Hover effect on rows */
        .dt-row:hover {
            background-color: #f5f5f5 !important;
        }
        
        /* Currency column alignment */
        .dt-cell--col-currency {
            text-align: right !important;
        }
        
        /* Percentage column styling */
        .dt-cell--col-percent {
            text-align: center !important;
        }
    `;
    document.head.appendChild(style);
}

// Chart view for visual representation
frappe.query_reports["TOTAL SALES REPORT"].chart = {
    type: 'bar',
    options: {
        title: 'Sales Performance by Distributor',
        height: 300,
        axisTitles: {
            x: 'Distributor',
            y: 'Amount (₹)'
        }
    },
    datasets: [
        {
            name: 'Current Sales',
            chartType: 'bar'
        },
        {
            name: 'Target',
            chartType: 'bar'
        },
        {
            name: 'Last Year',
            chartType: 'line'
        }
    ]
};

// Dynamic chart data generation
frappe.query_reports["TOTAL SALES REPORT"].get_chart_data = function(columns, result) {
    if (!result || result.length < 2) return null;
    
    // Get YTD row (second last) or last month
    let ytd_row = result.find(row => row.month === "TOTAL YTD");
    if (!ytd_row) ytd_row = result[result.length - 2] || result[0];
    
    let labels = [];
    let sales_data = [];
    let target_data = [];
    let ly_data = [];
    
    let distributors = ['agarwal', 'agrawal', 'bhagat', 'hindustan'];
    let dist_labels = ['Agarwal', 'Agrawal', 'Bhagat', 'Hindustan'];
    
    distributors.forEach((dist, idx) => {
        labels.push(dist_labels[idx]);
        sales_data.push(ytd_row[`${dist}_sales`] || 0);
        target_data.push(ytd_row[`${dist}_target`] || 0);
        ly_data.push(ytd_row[`${dist}_ly`] || 0);
    });
    
    return {
        labels: labels,
        datasets: [
            {
                name: 'Current Sales',
                values: sales_data
            },
            {
                name: 'Target',
                values: target_data
            },
            {
                name: 'Last Year',
                values: ly_data
            }
        ]
    };
};

// Export function for the report
frappe.query_reports["TOTAL SALES REPORT"].export = function(report) {
    export_to_excel(report);
};

// Auto-refresh every 5 minutes if enabled
frappe.query_reports["TOTAL SALES REPORT"].refresh_interval = 300000; // 5 minutes