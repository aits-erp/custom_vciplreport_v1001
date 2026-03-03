// frappe.query_reports["Sales Person Report"] = {
//     filters: [
//         // ---------------- PERIOD TYPE ----------------
//         {
//             fieldname: "period_type",
//             label: "Period Type",
//             fieldtype: "Select",
//             options: ["Month", "Quarter", "Half Year"],
//             default: "Month",
//             reqd: 1
//         },

//         // ---------------- MONTH ----------------
//         {
//             fieldname: "month",
//             label: "Month",
//             fieldtype: "Select",
//             options: [
//                 { label: "January", value: 1 },
//                 { label: "February", value: 2 },
//                 { label: "March", value: 3 },
//                 { label: "April", value: 4 },
//                 { label: "May", value: 5 },
//                 { label: "June", value: 6 },
//                 { label: "July", value: 7 },
//                 { label: "August", value: 8 },
//                 { label: "September", value: 9 },
//                 { label: "October", value: 10 },
//                 { label: "November", value: 11 },
//                 { label: "December", value: 12 }
//             ],
//             default: new Date().getMonth() + 1,
//             depends_on: "eval:doc.period_type=='Month'"
//         },

//         // ---------------- QUARTER (FY STYLE) ----------------
//         {
//             fieldname: "quarter",
//             label: "Quarter",
//             fieldtype: "Select",
//             options: [
//                 { label: "Q1 (Apr–Jun)", value: "Q1" },
//                 { label: "Q2 (Jul–Sep)", value: "Q2" },
//                 { label: "Q3 (Oct–Dec)", value: "Q3" },
//                 { label: "Q4 (Jan–Mar)", value: "Q4" }
//             ],
//             default: "Q1",
//             depends_on: "eval:doc.period_type=='Quarter'"
//         },

//         // ---------------- HALF YEAR ----------------
//         {
//             fieldname: "half_year",
//             label: "Half Year",
//             fieldtype: "Select",
//             options: [
//                 { label: "H1 (Apr–Sep)", value: "H1" },
//                 { label: "H2 (Oct–Mar)", value: "H2" }
//             ],
//             default: "H1",
//             depends_on: "eval:doc.period_type=='Half Year'"
//         },

//         // ---------------- YEAR ----------------
//         {
//             fieldname: "year",
//             label: "Year",
//             fieldtype: "Select",
//             options: ["2023", "2024", "2025", "2026"],
//             default: new Date().getFullYear().toString(),
//             reqd: 1
//         },

//         // ---------------- REGION ----------------
//         {
//             fieldname: "custom_region",
//             label: "Region",
//             fieldtype: "Data"
//         },

//         // ---------------- LOCATION ----------------
//         {
//             fieldname: "custom_location",
//             label: "Location",
//             fieldtype: "Data"
//         },

//         // ---------------- TERRITORY (updated fieldname) ----------------
//         {
//             fieldname: "custom_territory_name",
//             label: "Territory",
//             fieldtype: "Data"
//         },

//         // ---------------- HEAD SALES PERSON ----------------
//         {
//             fieldname: "parent_sales_person",
//             label: "Head Sales Person",
//             fieldtype: "Link",
//             options: "Sales Person"
//         },

//         // ---------------- CUSTOMER ----------------
//         {
//             fieldname: "customer",
//             label: "Customer",
//             fieldtype: "Link",
//             options: "Customer"
//         }
//     ]
// };

frappe.query_reports["Sales Person Report"] = {
    filters: [
        // ... your existing filters ...
    ],
    
    // Add this new section for formatter and drill down
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "invoice_amount" && data && data.customer_name !== "TOTAL") {
            // Make the amount clickable (except for total row)
            value = `<a href="#" data-customer="${data.customer_name}" 
                     data-from-date="${data.from_date}" data-to-date="${data.to_date}"
                     onclick="show_invoice_details(event, '${data.customer_name}', 
                     '${data.from_date}', '${data.to_date}', '${data.sales_person}')">${value}</a>`;
        }
        return value;
    },
    
    // Add this function to handle the click and show popup
    "onload": function(report) {
        // Add the click handler function to the window object
        window.show_invoice_details = function(event, customer, from_date, to_date, sales_person) {
            event.preventDefault();
            
            // Create and show dialog
            const dialog = new frappe.ui.Dialog({
                title: __('Invoice Details'),
                size: 'large',
                fields: [
                    {
                        fieldtype: 'HTML',
                        fieldname: 'invoice_details',
                    }
                ],
                primary_action_label: __('Close'),
                primary_action: function() {
                    dialog.hide();
                }
            });
            
            // Show loading
            dialog.show();
            dialog.set_values({
                invoice_details: '<div class="text-muted text-center">Loading...</div>'
            });
            
            // Fetch invoice details
            frappe.call({
                method: "frappe.query_reports.get_invoice_details",
                args: {
                    customer: customer,
                    from_date: from_date,
                    to_date: to_date,
                    sales_person: sales_person
                },
                callback: function(response) {
                    if (response.message) {
                        let html = build_invoice_table(response.message);
                        dialog.fields_dict.invoice_details.$wrapper.html(html);
                    }
                }
            });
        };
        
        // Helper function to build invoice table
        function build_invoice_table(invoices) {
            let html = `
                <table class="table table-bordered table-hover">
                    <thead>
                        <tr>
                            <th>Invoice No</th>
                            <th>Posting Date</th>
                            <th>Customer</th>
                            <th>Amount</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            invoices.forEach(inv => {
                html += `
                    <tr>
                        <td><a href="/app/sales-invoice/${inv.name}" target="_blank">${inv.name}</a></td>
                        <td>${inv.posting_date}</td>
                        <td>${inv.customer}</td>
                        <td class="text-right">${format_currency(inv.amount, inv.currency)}</td>
                        <td>${inv.status}</td>
                    </tr>
                `;
            });
            
            html += `
                    </tbody>
                    <tfoot>
                        <tr>
                            <th colspan="3" class="text-right">Total:</th>
                            <th class="text-right">${format_currency(invoices.reduce((sum, inv) => sum + inv.amount, 0))}</th>
                            <th></th>
                        </tr>
                    </tfoot>
                </table>
            `;
            
            return html;
        }
    }
};

