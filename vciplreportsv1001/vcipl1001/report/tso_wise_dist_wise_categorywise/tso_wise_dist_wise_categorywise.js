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
        this.add_custom_styles();
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
    
    // Custom formatter for better visuals
    formatter: function(value, row, column, data, default_formatter) {
        if (column.fieldname.includes("_achieved")) {
            let target_field = column.fieldname.replace("_achieved", "_target");
            let target = row[target_field] || 0;
            let percentage = target > 0 ? (value / target * 100) : 0;
            
            if (value > 0 && value >= target) {
                return `<span style="color: #28a745; font-weight: bold; background: #d4edda; padding: 4px 8px; border-radius: 4px;">
                            ${default_formatter(value, row, column, data)}
                            <small style="color: #155724;"> (${Math.round(percentage)}%)</small>
                        </span>`;
            } else if (value > 0 && value < target) {
                return `<span style="color: #ffc107; font-weight: bold; background: #fff3cd; padding: 4px 8px; border-radius: 4px;">
                            ${default_formatter(value, row, column, data)}
                            <small style="color: #856404;"> (${Math.round(percentage)}%)</small>
                        </span>`;
            } else if (value === 0 && target > 0) {
                return `<span style="color: #dc3545; background: #f8d7da; padding: 4px 8px; border-radius: 4px;">
                            ${default_formatter(value, row, column, data)}
                            <small style="color: #721c24;"> (0%)</small>
                        </span>`;
            }
            return default_formatter(value, row, column, data);
        }
        
        if (column.fieldname.includes("_target")) {
            return `<span style="color: #6c757d; font-style: italic;">🎯 ${default_formatter(value, row, column, data)}</span>`;
        }
        
        if (column.fieldname === "total_achieved") {
            return `<strong style="color: #28a745;">${default_formatter(value, row, column, data)}</strong>`;
        }
        
        if (column.fieldname === "total_target") {
            return `<strong style="color: #ffc107;">🎯 ${default_formatter(value, row, column, data)}</strong>`;
        }
        
        if (column.fieldname === "achievement_percentage") {
            let color = value >= 100 ? "#28a745" : (value >= 60 ? "#ffc107" : "#dc3545");
            return `<div style="text-align: center;">
                        <div class="progress" style="background-color: #e9ecef; border-radius: 10px; height: 8px; margin-bottom: 5px;">
                            <div style="width: ${Math.min(value, 100)}%; background-color: ${color}; height: 8px; border-radius: 10px;"></div>
                        </div>
                        <strong style="color: ${color};">${Math.round(value)}%</strong>
                    </div>`;
        }
        
        return default_formatter(value, row, column, data);
    },
    
    add_custom_styles: function() {
        let style = document.createElement('style');
        style.innerHTML = `
            .report-table {
                border-collapse: separate;
                border-spacing: 0 8px;
            }
            .report-table tbody tr {
                background: white;
                transition: all 0.3s ease;
            }
            .report-table tbody tr:hover {
                transform: scale(1.01);
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .report-table th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                font-weight: 600;
            }
            .report-table td {
                padding: 10px;
                vertical-align: middle;
            }
            .progress {
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }
        `;
        document.head.appendChild(style);
    }
};