// frappe.query_reports["TSO WISE CATEGORYWISE"] = {
//     onload: function(report) {
//         // Set default category filter
//         report.set_filter_value("custom_main_group", [
//             "Hard Anodised",
//             "Nonstick",
//             "Horeca",
//             "Pressure Cookers",
//             "SS Cookware",
//             "Healux",
//             "Kraft",
//             "Platinum",
//             "Platinum Triply P.cooker",
//             "Cast Iron",
//             "Kraft Pressure Cooker",
//             "Csd",
//             "Cookers Spare Parts",
//             "Other Spare"
//         ]);
//     },

//     filters: [
//         {
//             fieldname: "from_date",
//             label: "From Date",
//             fieldtype: "Date",
//             default: frappe.datetime.month_start(),
//             reqd: 1
//         },
//         {
//             fieldname: "to_date",
//             label: "To Date",
//             fieldtype: "Date",
//             default: frappe.datetime.month_end(),
//             reqd: 1
//         },
//         {
//             fieldname: "sales_person",
//             label: "TSO",
//             fieldtype: "Link",
//             options: "Sales Person"
//         },
//         {
//             fieldname: "parent_sales_person",
//             label: "Head Sales Person",
//             fieldtype: "Link",
//             options: "Sales Person"
//         },
//         {
//             fieldname: "custom_region",
//             label: "Region",
//             fieldtype: "MultiSelectList",
//             get_data: function(txt) {
//                 return frappe.db.sql_list(`
//                     SELECT DISTINCT custom_region
//                     FROM \`tabSales Person\`
//                     WHERE custom_region IS NOT NULL
//                     AND custom_region != ''
//                     AND custom_region LIKE %s
//                 `, ["%" + txt + "%"]);
//             }
//         },
//         {
//             fieldname: "custom_head_sales_code",
//             label: "Head Sales Code",
//             fieldtype: "MultiSelectList",
//             get_data: function(txt) {
//                 return frappe.db.sql_list(`
//                     SELECT DISTINCT custom_head_sales_code
//                     FROM \`tabSales Person\`
//                     WHERE custom_head_sales_code IS NOT NULL
//                     AND custom_head_sales_code != ''
//                     AND custom_head_sales_code LIKE %s
//                 `, ["%" + txt + "%"]);
//             }
//         },
//         {
//             fieldname: "customer",
//             label: "Customer",
//             fieldtype: "Link",
//             options: "Customer"
//         },
//         {
//             fieldname: "customer_group",
//             label: "Customer Group",
//             fieldtype: "Link",
//             options: "Customer Group"
//         },
//         {
//             fieldname: "custom_main_group",
//             label: "Category",
//             fieldtype: "MultiSelectList",
//             get_data: function(txt) {
//                 return frappe.db.sql_list(`
//                     SELECT DISTINCT custom_main_group
//                     FROM \`tabItem\`
//                     WHERE custom_main_group IS NOT NULL
//                     AND custom_main_group != ''
//                     AND custom_main_group LIKE %s
//                 `, ["%" + txt + "%"]);
//             }
//         }
//     ],
    
//     // Add formatter for better visual representation
//     formatter: function(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);
        
//         // Format currency columns with colors
//         if (column.fieldname.includes("_achieved")) {
//             if (parseFloat(value) > 0) {
//                 value = `<span style="color: #28a745; font-weight: 600;">${value}</span>`;
//             } else if (parseFloat(value) === 0) {
//                 value = `<span style="color: #dc3545;">${value}</span>`;
//             }
//         }
        
//         // Format target columns with different color
//         if (column.fieldname.includes("_target")) {
//             if (parseFloat(value) > 0) {
//                 value = `<span style="color: #007bff; font-weight: 600;">${value}</span>`;
//             }
//         }
        
//         return value;
//     }
// };
frappe.query_reports["TSO WISE CATEGORYWISE"] = {
    onload: function(report) {
        report.set_filter_value("custom_main_group", [
        "Hard Anodised","Nonstick","Horeca","Pressure Cookers",
        "SS Cookware","Healux","Kraft","Platinum",
        "Platinum Triply P.cooker","Cast Iron","Bottle",
        "Kraft Pressure Cooker","Electrical Appliances","Csd",
        "Raw Material","Scrap","Cookers Spare Parts","Circle",
        "Other Spare","Carton","SFG","Sticker & Warranty Card",
        "Trading SFG","Machinery Spare Parts","Tool","Bag",
        "Powder","Machinery","Spoons","Polishing","Other",
        "Coil","Assorted Utensils","Futuretec"
         ]);
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
        },

        // ✅ CHECKBOX
        {
            fieldname: "show_item_details",
            label: "Include Item Code & Item Name",
            fieldtype: "Check",
            default: 0
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname.includes("_achieved")) {
            if (parseFloat(value) > 0) {
                value = `<span style="color:#28a745;font-weight:600;">${value}</span>`;
            } else if (parseFloat(value) === 0) {
                value = `<span style="color:#dc3545;">${value}</span>`;
            }
        }

        if (column.fieldname.includes("_target")) {
            if (parseFloat(value) > 0) {
                value = `<span style="color:#007bff;font-weight:600;">${value}</span>`;
            }
        }

        return value;
    }
};