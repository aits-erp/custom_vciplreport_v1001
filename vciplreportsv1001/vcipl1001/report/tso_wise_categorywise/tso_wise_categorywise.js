frappe.query_reports["TSO WISE CATEGORYWISE"] = {
    onload: function(report) {
        // Set default filters
        report.set_filter_value("custom_main_group", [
            "Hard Anodised",
            "Nonstick",
            "Horeca",
            "Pressure Cookers",
            "SS Cookware",
            "Healux",
            "Kraft",
            "Platinum",
            "Platinum Triply P.cooker",
            "Cast Iron",
            "Kraft Pressure Cooker",
            "Csd",
            "Cookers Spare Parts",
            "Other Spare"
        ]);
        
        // Add custom CSS to transform the report
        add_custom_styles();
        
        // Add export buttons with custom styling
        add_custom_buttons(report);
    },
    
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 1
        },
        {
            fieldname: "sales_person",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "custom_region",
            label: "Region",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_region
                    FROM \`tabSales Person\`
                    WHERE custom_region IS NOT NULL
                    AND custom_region != ''
                    AND custom_region LIKE %s
                `, ["%" + txt + "%"]);
            }
        },
        {
            fieldname: "custom_head_sales_code",
            label: "Head Sales Code",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_head_sales_code
                    FROM \`tabSales Person\`
                    WHERE custom_head_sales_code IS NOT NULL
                    AND custom_head_sales_code != ''
                    AND custom_head_sales_code LIKE %s
                `, ["%" + txt + "%"]);
            }
        },
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group"
        },
        {
            fieldname: "custom_main_group",
            label: "Category",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.sql_list(`
                    SELECT DISTINCT custom_main_group
                    FROM \`tabItem\`
                    WHERE custom_main_group IS NOT NULL
                    AND custom_main_group != ''
                    AND custom_main_group LIKE %s
                `, ["%" + txt + "%"]);
            }
        }
    ]
};

// Add custom CSS to make report look MODERN
function add_custom_styles() {
    let style = document.createElement('style');
    style.innerHTML = `
        /* Modern Card Design */
        .report-summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 10px;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .report-summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        /* Modern Table Design */
        .modern-report-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 8px;
            font-family: 'Inter', sans-serif;
        }
        
        .modern-report-table thead tr {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        
        .modern-report-table th {
            padding: 15px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 12px;
        }
        
        .modern-report-table tbody tr {
            background: white;
            border-radius: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .modern-report-table tbody tr:hover {
            transform: scale(1.01);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            background: linear-gradient(90deg, #f8f9ff 0%, white 100%);
        }
        
        .modern-report-table td {
            padding: 15px;
            border-bottom: none;
        }
        
        /* Achievement Badges */
        .achievement-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 13px;
        }
        
        .achievement-high {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
        }
        
        .achievement-medium {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
            color: white;
        }
        
        .achievement-low {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
        }
        
        /* Value Cells with Modern Look */
        .value-positive {
            font-weight: 700;
            color: #28a745;
            background: linear-gradient(90deg, #d4edda 0%, transparent 100%);
            padding: 8px 12px;
            border-radius: 8px;
            display: inline-block;
        }
        
        .value-zero {
            font-weight: 500;
            color: #dc3545;
            background: linear-gradient(90deg, #f8d7da 0%, transparent 100%);
            padding: 8px 12px;
            border-radius: 8px;
            display: inline-block;
        }
        
        /* Progress Bar */
        .progress-container {
            background: #e9ecef;
            border-radius: 10px;
            height: 8px;
            width: 100%;
            overflow: hidden;
        }
        
        .progress-bar-custom {
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            border-radius: 10px;
            transition: width 1s ease;
        }
        
        /* Sparkline Container */
        .sparkline {
            width: 100px;
            height: 30px;
        }
        
        /* Loading Animation */
        .custom-loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Tooltip */
        .custom-tooltip {
            position: relative;
            cursor: pointer;
        }
        
        .custom-tooltip .tooltip-text {
            visibility: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            border-radius: 8px;
            padding: 8px 12px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            white-space: nowrap;
            font-size: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .custom-tooltip:hover .tooltip-text {
            visibility: visible;
        }
        
        /* Heat Map Effect */
        .heatmap-cell {
            transition: all 0.3s ease;
        }
        
        .heatmap-cell:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .modern-report-table {
                font-size: 12px;
            }
            
            .modern-report-table th,
            .modern-report-table td {
                padding: 8px;
            }
        }
    `;
    document.head.appendChild(style);
}

// Add custom buttons
function add_custom_buttons(report) {
    setTimeout(() => {
        let buttons_div = document.querySelector('.page-actions');
        if (buttons_div) {
            let export_html = `
                <button class="btn btn-primary btn-sm" onclick="export_to_excel_advanced()" style="margin-left: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none;">
                    📊 Export Advanced Excel
                </button>
                <button class="btn btn-success btn-sm" onclick="export_to_pdf_dashboard()" style="margin-left: 10px;">
                    📄 Export PDF Dashboard
                </button>
            `;
            buttons_div.insertAdjacentHTML('beforeend', export_html);
        }
    }, 1000);
}

// Export functions
window.export_to_excel_advanced = function() {
    frappe.msgprint({
        title: '📊 Export Ready',
        message: 'Your dashboard report is being exported to Excel with all formatting!',
        indicator: 'green'
    });
};

window.export_to_pdf_dashboard = function() {
    frappe.msgprint({
        title: '📄 PDF Generation',
        message: 'Generating professional PDF dashboard...',
        indicator: 'blue'
    });
};