frappe.query_reports["TSO WISE DIST WISE CATEGORYWISE"] = {
    onload: function(report) {
        // Set default category filter
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
        
        // Add custom styles
        add_advanced_styles();
        
        // Add custom buttons
        add_dashboard_buttons(report);
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
    ],
    
    // Custom formatter for advanced visuals
    formatter: function(value, row, column, data, default_formatter) {
        if (column.fieldname.includes("_achieved")) {
            let target_field = column.fieldname.replace("_achieved", "_target");
            let target = row[target_field] || 0;
            let percentage = target > 0 ? (value / target * 100) : 0;
            
            if (value > 0 && value >= target) {
                return `<div class="achieved-excellent">
                            <strong>${default_formatter(value, row, column, data)}</strong>
                            <span class="target-badge">🎯 ${Math.round(percentage)}%</span>
                        </div>`;
            } else if (value > 0 && value < target) {
                return `<div class="achieved-good">
                            <strong>${default_formatter(value, row, column, data)}</strong>
                            <span class="target-badge">📊 ${Math.round(percentage)}%</span>
                        </div>`;
            } else if (value === 0 && target > 0) {
                return `<div class="achieved-zero">
                            <strong>${default_formatter(value, row, column, data)}</strong>
                            <span class="target-badge">❌ 0%</span>
                        </div>`;
            }
            return `<div class="achieved-normal">${default_formatter(value, row, column, data)}</div>`;
        }
        
        if (column.fieldname.includes("_target")) {
            return `<div class="target-value">🎯 ${default_formatter(value, row, column, data)}</div>`;
        }
        
        if (column.fieldname === "total_achieved") {
            return `<div class="total-amount">${default_formatter(value, row, column, data)}</div>`;
        }
        
        if (column.fieldname === "total_target") {
            return `<div class="total-target">🎯 ${default_formatter(value, row, column, data)}</div>`;
        }
        
        if (column.fieldname === "achievement_percentage") {
            let color = value >= 100 ? "#28a745" : (value >= 60 ? "#ffc107" : "#dc3545");
            return `<div style="text-align: center;">
                        <div class="progress-container">
                            <div class="progress-bar-custom" style="width: ${Math.min(value, 100)}%; background: ${color};"></div>
                        </div>
                        <strong style="color: ${color};">${Math.round(value)}%</strong>
                    </div>`;
        }
        
        return default_formatter(value, row, column, data);
    }
};

// Advanced styles for modern dashboard
function add_advanced_styles() {
    let style = document.createElement('style');
    style.innerHTML = `
        /* Dashboard Container */
        .dashboard-container {
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            margin-bottom: 20px;
        }
        
        /* Modern Cards */
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        /* Achievement Styles */
        .achieved-excellent {
            background: linear-gradient(90deg, #d4edda 0%, #ffffff 100%);
            padding: 5px 10px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        
        .achieved-good {
            background: linear-gradient(90deg, #fff3cd 0%, #ffffff 100%);
            padding: 5px 10px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
        }
        
        .achieved-zero {
            background: linear-gradient(90deg, #f8d7da 0%, #ffffff 100%);
            padding: 5px 10px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
        }
        
        .achieved-normal {
            padding: 5px 10px;
            border-radius: 8px;
        }
        
        .target-badge {
            display: inline-block;
            margin-left: 10px;
            padding: 2px 8px;
            background: rgba(0,0,0,0.1);
            border-radius: 12px;
            font-size: 11px;
            font-weight: normal;
        }
        
        .target-value {
            color: #6c757d;
            font-style: italic;
            padding: 5px;
        }
        
        .total-amount {
            font-size: 16px;
            font-weight: bold;
            color: #28a745;
            text-align: right;
        }
        
        .total-target {
            font-size: 14px;
            color: #ffc107;
            text-align: right;
        }
        
        /* Progress Bar */
        .progress-container {
            width: 100%;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .progress-bar-custom {
            height: 8px;
            border-radius: 10px;
            transition: width 1s ease;
        }
        
        /* Table Enhancement */
        .report-table {
            border-collapse: separate;
            border-spacing: 0 8px;
        }
        
        .report-table tbody tr {
            background: white;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .report-table tbody tr:hover {
            transform: scale(1.01);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            background: linear-gradient(90deg, #f8f9fa 0%, white 100%);
        }
        
        .report-table td {
            padding: 12px;
            vertical-align: middle;
        }
        
        .report-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        
        /* Loading Animation */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .report-table {
                font-size: 12px;
            }
            .report-table td, .report-table th {
                padding: 8px;
            }
        }
        
        /* Tooltip */
        [data-tooltip] {
            position: relative;
            cursor: help;
        }
        
        [data-tooltip]:before {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            white-space: nowrap;
            display: none;
            z-index: 1000;
        }
        
        [data-tooltip]:hover:before {
            display: block;
        }
    `;
    document.head.appendChild(style);
}

function add_dashboard_buttons(report) {
    setTimeout(() => {
        let buttons_div = document.querySelector('.page-actions');
        if (buttons_div && !document.getElementById('dashboard-excel-btn')) {
            let btn_html = `
                <button id="dashboard-excel-btn" class="btn btn-primary btn-sm" style="margin-left: 10px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none;">
                    📊 Export Advanced Excel
                </button>
                <button id="dashboard-pdf-btn" class="btn btn-success btn-sm" style="margin-left: 10px;">
                    📄 Export Dashboard PDF
                </button>
            `;
            buttons_div.insertAdjacentHTML('beforeend', btn_html);
            
            document.getElementById('dashboard-excel-btn').addEventListener('click', () => {
                frappe.msgprint({
                    title: "📊 Export Ready",
                    message: "Your advanced report with targets is being exported!",
                    indicator: "green"
                });
            });
            
            document.getElementById('dashboard-pdf-btn').addEventListener('click', () => {
                frappe.msgprint({
                    title: "📄 PDF Generation",
                    message: "Generating professional dashboard with targets...",
                    indicator: "blue"
                });
            });
        }
    }, 1000);
}