// frappe/your_app/your_app/report/comprehensive_sales_report/comprehensive_sales_report.js

frappe.query_reports["Sales Person Report Monthwise"] = {
    filters: [
        // Common Filters
        {
            fieldname: "report_type",
            label: "Report Type",
            fieldtype: "Select",
            options: ["Item Category Wise", "Sales Person Wise", "Combined View"],
            default: "Combined View",
            reqd: 1
        },
        
        // Date Filters
        { 
            fieldname: "from_date", 
            label: "From Date", 
            fieldtype: "Date", 
            default: frappe.datetime.year_start(),
            reqd: 1 
        },
        { 
            fieldname: "to_date", 
            label: "To Date", 
            fieldtype: "Date", 
            default: frappe.datetime.year_end(),
            reqd: 1 
        },
        
        // Period Type (for Sales Person View)
        {
            fieldname: "period_type",
            label: "Period Type",
            fieldtype: "Select",
            options: ["Month", "Quarter", "Half Year"],
            default: "Month",
            depends_on: "eval:doc.report_type!='Item Category Wise'"
        },
        
        // Month
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: [
                { label: "January", value: 1 },
                { label: "February", value: 2 },
                { label: "March", value: 3 },
                { label: "April", value: 4 },
                { label: "May", value: 5 },
                { label: "June", value: 6 },
                { label: "July", value: 7 },
                { label: "August", value: 8 },
                { label: "September", value: 9 },
                { label: "October", value: 10 },
                { label: "November", value: 11 },
                { label: "December", value: 12 }
            ],
            default: new Date().getMonth() + 1,
            depends_on: "eval:doc.period_type=='Month' && doc.report_type!='Item Category Wise'"
        },
        
        // Quarter
        {
            fieldname: "quarter",
            label: "Quarter",
            fieldtype: "Select",
            options: [
                { label: "Q1 (Apr–Jun)", value: "Q1" },
                { label: "Q2 (Jul–Sep)", value: "Q2" },
                { label: "Q3 (Oct–Dec)", value: "Q3" },
                { label: "Q4 (Jan–Mar)", value: "Q4" }
            ],
            default: "Q1",
            depends_on: "eval:doc.period_type=='Quarter' && doc.report_type!='Item Category Wise'"
        },
        
        // Half Year
        {
            fieldname: "half_year",
            label: "Half Year",
            fieldtype: "Select",
            options: [
                { label: "H1 (Apr–Sep)", value: "H1" },
                { label: "H2 (Oct–Mar)", value: "H2" }
            ],
            default: "H1",
            depends_on: "eval:doc.period_type=='Half Year' && doc.report_type!='Item Category Wise'"
        },
        
        // Year
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: ["2023", "2024", "2025", "2026"],
            default: new Date().getFullYear().toString(),
            depends_on: "eval:doc.report_type!='Item Category Wise'"
        },
        
        // Item Related Filters
        { 
            fieldname: "item_group", 
            label: "Item Group", 
            fieldtype: "Link", 
            options: "Item Group" 
        },
        { 
            fieldname: "custom_main_group", 
            label: "Main Group", 
            fieldtype: "Data" 
        },
        { 
            fieldname: "custom_sub_group", 
            label: "Sub Group", 
            fieldtype: "Data" 
        },
        { 
            fieldname: "custom_item_type", 
            label: "Item Type", 
            fieldtype: "Data" 
        },
        
        // Sales Person Related Filters
        { 
            fieldname: "parent_sales_person", 
            label: "Head Sales Person", 
            fieldtype: "Link", 
            options: "Sales Person" 
        },
        { 
            fieldname: "custom_region", 
            label: "Region", 
            fieldtype: "Data" 
        },
        { 
            fieldname: "custom_location", 
            label: "Location", 
            fieldtype: "Data" 
        },
        { 
            fieldname: "custom_territory", 
            label: "Territory", 
            fieldtype: "Data" 
        },
        
        // Customer Filter
        { 
            fieldname: "customer", 
            label: "Customer", 
            fieldtype: "Link", 
            options: "Customer" 
        }
    ],

    onload: function(report) {
        // Add custom tabs for better UX
        report.page.add_inner_button(__("Item Category View"), function() {
            report.set_filter_value("report_type", "Item Category Wise");
        });
        
        report.page.add_inner_button(__("Sales Person View"), function() {
            report.set_filter_value("report_type", "Sales Person Wise");
        });
        
        report.page.add_inner_button(__("Combined View"), function() {
            report.set_filter_value("report_type", "Combined View");
        });
    },

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Keep the popup functionality from item report
        if (data.popup_data && ["item_group", "custom_main_group", "custom_sub_group"].includes(column.fieldname)) {
            if (data[column.fieldname] > 0) {
                value = `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
                    onclick='frappe.query_reports["Comprehensive Sales Report"]
                    .show_item_popup("${column.fieldname}", ${data.popup_data})'>
                    ${value}
                </a>`;
            }
        }
        
        return value;
    },

    show_item_popup(customer_field, popup_data) {
        let rows = popup_data[customer_field] || [];
        
        let html = `
        <div>
            <table class="table table-bordered">
                <tr>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Amount</th>
                </tr>`;
        
        rows.forEach(r => {
            let bold = r.item_name.includes("Total") ? "font-weight:bold;background:#f7f7f7" : "";
            html += `
                <tr style="${bold}">
                    <td>${r.item_name}</td>
                    <td>${r.qty}</td>
                    <td>${r.amount}</td>
                </tr>`;
        });
        
        html += `</table></div>`;
        
        frappe.msgprint({
            title: "Item Breakdown",
            message: html,
            wide: true
        });
    }
};
