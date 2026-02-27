// tso_wise_dist_wise_categorywise.js
// eslint-disable-next-line
frappe.query_reports["TSO WISE DIST WISE CATEGORYWISE"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "tso_name",
            "label": __("TSO Name"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "get_query": function() {
                return {
                    filters: {
                        "enabled": 1
                    }
                };
            },
            "onchange": function(report) {
                // When TSO changes, update distributor filter options
                let tso_name = report.get_values().tso_name;
                if (tso_name) {
                    frappe.call({
                        method: "your_app.your_app.report.tso_wise_dist_wise_categorywise.tso_wise_dist_wise_categorywise.get_distributors_for_tso",
                        args: { tso_name: tso_name },
                        callback: function(r) {
                            let distributor_filter = report.get_filter("distributor");
                            if (r.message) {
                                distributor_filter.df.options = r.message;
                                distributor_filter.refresh();
                            }
                        }
                    });
                }
            }
        },
        {
            "fieldname": "distributor",
            "label": __("Distributor"),
            "fieldtype": "Link",
            "options": "Customer"
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
            ]
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Format percentage columns with color coding
        if (column.fieldname.includes("_pct")) {
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
                    value = `<span style="font-weight: 600; color: #1e446d;">${value}</span>`;
                }
            }
        }
        
        // Highlight total row
        if (data.month === "TOTAL YTD") {
            if (column.fieldname === "month") {
                value = `<span style="font-weight: bold; font-size: 12px; color: #1e446d;">${value}</span>`;
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
        
        report.page.add_inner_button(__("TSO Comparison"), function() {
            show_tso_comparison(report);
        });
        
        report.page.add_inner_button(__("Distributor Breakdown"), function() {
            show_distributor_breakdown(report);
        });
        
        // Add note about "TOTAL OF ALL DIST LINKED TO THIS TSO"
        setTimeout(() => {
            let note = $(`
                <div class="alert alert-info" style="margin: 10px 15px; padding: 8px 15px;">
                    <i class="fa fa-info-circle"></i> 
                    <strong>Note:</strong> This report shows TOTAL OF ALL DISTRIBUTORS linked to each TSO
                </div>
            `);
            report.page.main.find(".page-content").prepend(note);
        }, 500);
    },

    "after_datatable_render": function(report) {
        // Add custom styling
        setTimeout(function() {
            add_custom_styling();
        }, 100);
    }
};

// Export to Excel function
function export_to_excel(report) {
    let data = report.data;
    let columns = report.columns;
    
    if (!data || data.length === 0) {
        frappe.msgprint(__("No data to export"));
        return;
    }
    
    let wb_data = [];
    
    // Add headers
    let headers = columns.map(col => col.label);
    wb_data.push(headers);
    
    // Add data rows
    data.forEach(row => {
        let row_data = columns.map(col => {
            let val = row[col.fieldname] || 0;
            if (col.fieldtype === "Currency" && val !== 0) {
                return val;
            }
            return val;
        });
        wb_data.push(row_data);
    });
    
    // Create CSV with UTF-8 BOM for Excel
    let csv_content = wb_data.map(row => 
        row.map(cell => {
            if (typeof cell === 'string' && cell.includes(',')) {
                return `"${cell}"`;
            }
            return cell;
        }).join(',')
    ).join('\n');
    
    let blob = new Blob(["\uFEFF" + csv_content], { type: 'text/csv;charset=utf-8;' });
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = `tso_dist_wise_${frappe.datetime.nowdate()}.csv`;
    a.click();
    
    frappe.show_alert({
        message: __("Report exported successfully"),
        indicator: "green"
    });
}

// Show TSO comparison dialog
function show_tso_comparison(report) {
    let data = report.data;
    if (!data || data.length < 2) {
        frappe.msgprint(__("Insufficient data for comparison"));
        return;
    }
    
    // Get YTD row
    let ytd_row = data.find(row => row.month === "TOTAL YTD");
    if (!ytd_row) ytd_row = data[data.length - 1];
    
    let dialog = new frappe.ui.Dialog({
        title: __("TSO Performance Comparison"),
        size: "extra-large",
        fields: [
            {
                fieldtype: "HTML",
                fieldname: "comparison_html",
                options: `
                    <div style="padding: 20px;">
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px;">
                            ${generate_tso_cards(ytd_row)}
                        </div>
                        
                        <h5 style="margin: 20px 0 15px; color: #495057;">Performance Metrics by TSO</h5>
                        
                        <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                    <th style="padding: 15px; text-align: left;">TSO</th>
                                    <th style="padding: 15px; text-align: right;">Total Sales</th>
                                    <th style="padding: 15px; text-align: right;">Total Target</th>
                                    <th style="padding: 15px; text-align: center;">Achievement</th>
                                    <th style="padding: 15px; text-align: right;">Last Year</th>
                                    <th style="padding: 15px; text-align: center;">Growth</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${generate_comparison_rows(ytd_row)}
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

// Generate TSO metric cards
function generate_tso_cards(ytd_row) {
    let tsos = [
        {name: "VINOD LEGACY", sales: ytd_row.vinod_sales || 0, target: ytd_row.vinod_target || 0, pct: ytd_row.vinod_pct || 0},
        {name: "PLATINUM", sales: ytd_row.platinum_sales || 0, target: ytd_row.platinum_target || 0, pct: ytd_row.platinum_pct || 0},
        {name: "PC Inner Lid", sales: ytd_row.inner_sales || 0, target: ytd_row.inner_target || 0, pct: ytd_row.inner_pct || 0},
        {name: "PC Outer Lid", sales: ytd_row.outer_sales || 0, target: ytd_row.outer_target || 0, pct: ytd_row.outer_pct || 0}
    ];
    
    let cards = '';
    tsos.forEach(tso => {
        let color = tso.pct >= 100 ? '#28a745' : (tso.pct >= 80 ? '#ffc107' : '#dc3545');
        cards += `
            <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;">
                <div style="font-size: 16px; font-weight: 600; color: #2c3e50; margin-bottom: 15px;">${tso.name}</div>
                <div style="font-size: 24px; font-weight: bold; color: #1e446d; margin-bottom: 10px;">₹${format_number(tso.sales)}</div>
                <div style="display: flex; justify-content: space-between; font-size: 13px; color: #6c757d; margin-bottom: 10px;">
                    <span>Target: ₹${format_number(tso.target)}</span>
                    <span>Gap: ₹${format_number(tso.target - tso.sales)}</span>
                </div>
                <div style="background: #f8f9fa; height: 30px; border-radius: 15px; overflow: hidden; margin-top: 10px;">
                    <div style="background: ${color}; width: ${Math.min(tso.pct, 100)}%; height: 100%; text-align: center; line-height: 30px; color: white; font-weight: bold;">
                        ${tso.pct}%
                    </div>
                </div>
            </div>
        `;
    });
    
    return cards;
}

// Generate comparison rows
function generate_comparison_rows(ytd_row) {
    let tsos = [
        {name: "VINOD LEGACY", sales: ytd_row.vinod_sales || 0, target: ytd_row.vinod_target || 0, 
         ly: ytd_row.vinod_ly || 0, pct: ytd_row.vinod_pct || 0},
        {name: "PLATINUM", sales: ytd_row.platinum_sales || 0, target: ytd_row.platinum_target || 0,
         ly: ytd_row.platinum_ly || 0, pct: ytd_row.platinum_pct || 0},
        {name: "PC Inner Lid", sales: ytd_row.inner_sales || 0, target: ytd_row.inner_target || 0,
         ly: ytd_row.inner_ly || 0, pct: ytd_row.inner_pct || 0},
        {name: "PC Outer Lid", sales: ytd_row.outer_sales || 0, target: ytd_row.outer_target || 0,
         ly: ytd_row.outer_ly || 0, pct: ytd_row.outer_pct || 0}
    ];
    
    let rows = '';
    tsos.forEach((tso, index) => {
        let growth = tso.ly ? ((tso.sales - tso.ly) / tso.ly * 100).toFixed(1) : 0;
        let growth_color = growth >= 0 ? '#28a745' : '#dc3545';
        let bg_color = index % 2 === 0 ? '#f8f9fa' : 'white';
        
        rows += `
            <tr style="background: ${bg_color}; border-bottom: 1px solid #dee2e6;">
                <td style="padding: 12px; text-align: left; font-weight: 500;">${tso.name}</td>
                <td style="padding: 12px; text-align: right;">₹${format_number(tso.sales)}</td>
                <td style="padding: 12px; text-align: right;">₹${format_number(tso.target)}</td>
                <td style="padding: 12px; text-align: center;">
                    <span style="background: ${tso.pct >= 100 ? '#28a745' : (tso.pct >= 80 ? '#ffc107' : '#dc3545')}; 
                         color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                        ${tso.pct}%
                    </span>
                </td>
                <td style="padding: 12px; text-align: right;">₹${format_number(tso.ly)}</td>
                <td style="padding: 12px; text-align: center;">
                    <span style="color: ${growth_color}; font-weight: bold;">
                        ${growth}%
                    </span>
                </td>
            </tr>
        `;
    });
    
    return rows;
}

// Show distributor breakdown for selected TSO
function show_distributor_breakdown(report) {
    let filters = report.get_values();
    let tso_name = filters.tso_name;
    
    if (!tso_name) {
        frappe.msgprint(__("Please select a TSO first"));
        return;
    }
    
    frappe.call({
        method: "your_app.your_app.report.tso_wise_dist_wise_categorywise.tso_wise_dist_wise_categorywise.get_distributors_for_tso",
        args: { tso_name: tso_name },
        callback: function(r) {
            if (!r.message || r.message.length === 0) {
                frappe.msgprint(__("No distributors found for this TSO"));
                return;
            }
            
            let distributors = r.message;
            let html = `
                <div style="padding: 20px;">
                    <h4 style="margin-bottom: 20px; color: #1e446d;">Distributors for ${tso_name}</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #4a5568; color: white;">
                                <th style="padding: 12px; text-align: left;">#</th>
                                <th style="padding: 12px; text-align: left;">Distributor Name</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${distributors.map((d, i) => `
                                <tr style="border-bottom: 1px solid #dee2e6;">
                                    <td style="padding: 10px;">${i+1}</td>
                                    <td style="padding: 10px;">${d.label}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            let dialog = new frappe.ui.Dialog({
                title: __("Distributor Breakdown"),
                size: "large",
                fields: [
                    {
                        fieldtype: "HTML",
                        fieldname: "dist_html",
                        options: html
                    }
                ],
                primary_action_label: __("Close"),
                primary_action: function() {
                    dialog.hide();
                }
            });
            
            dialog.show();
        }
    });
}

// Format number helper
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

// Add custom CSS styling
function add_custom_styling() {
    let style = document.createElement('style');
    style.innerHTML = `
        .dt-row.dt-row-header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%) !important;
            color: white !important;
        }
        
        .dt-row.dt-row-header .dt-cell {
            color: white !important;
            font-weight: 600;
        }
        
        .dt-cell {
            border-right: 1px solid #e9ecef;
            padding: 12px 8px !important;
        }
        
        .dt-cell:last-child {
            border-right: none;
        }
        
        tr[data-rowname="TOTAL YTD"] {
            background: linear-gradient(to right, #f8f9fa, #e9ecef) !important;
            font-weight: 600;
            border-top: 2px solid #2c3e50;
            border-bottom: 2px solid #2c3e50;
        }
        
        .dt-row:hover {
            background-color: #f1f3f5 !important;
            transition: background-color 0.2s;
        }
        
        /* Style for the info note */
        .alert-info {
            border-left: 4px solid #17a2b8;
            background-color: #e7f5ff;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .dt-cell {
                font-size: 11px;
                padding: 8px 4px !important;
            }
        }
    `;
    document.head.appendChild(style);
}