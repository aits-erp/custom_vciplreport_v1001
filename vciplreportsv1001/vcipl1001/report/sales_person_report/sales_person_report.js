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

// Copyright (c) 2024, your company and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person Report"] = {
    filters: [
        // ---------------- PERIOD TYPE ----------------
        {
            fieldname: "period_type",
            label: __("Period Type"),
            fieldtype: "Select",
            options: ["Month", "Quarter", "Half Year"],
            default: "Month",
            reqd: 1
        },

        // ---------------- MONTH ----------------
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { label: __("January"), value: 1 },
                { label: __("February"), value: 2 },
                { label: __("March"), value: 3 },
                { label: __("April"), value: 4 },
                { label: __("May"), value: 5 },
                { label: __("June"), value: 6 },
                { label: __("July"), value: 7 },
                { label: __("August"), value: 8 },
                { label: __("September"), value: 9 },
                { label: __("October"), value: 10 },
                { label: __("November"), value: 11 },
                { label: __("December"), value: 12 }
            ],
            default: new Date().getMonth() + 1,
            depends_on: "eval:doc.period_type=='Month'"
        },

        // ---------------- QUARTER (FY STYLE) ----------------
        {
            fieldname: "quarter",
            label: __("Quarter"),
            fieldtype: "Select",
            options: [
                { label: __("Q1 (Apr–Jun)"), value: "Q1" },
                { label: __("Q2 (Jul–Sep)"), value: "Q2" },
                { label: __("Q3 (Oct–Dec)"), value: "Q3" },
                { label: __("Q4 (Jan–Mar)"), value: "Q4" }
            ],
            default: "Q1",
            depends_on: "eval:doc.period_type=='Quarter'"
        },

        // ---------------- HALF YEAR ----------------
        {
            fieldname: "half_year",
            label: __("Half Year"),
            fieldtype: "Select",
            options: [
                { label: __("H1 (Apr–Sep)"), value: "H1" },
                { label: __("H2 (Oct–Mar)"), value: "H2" }
            ],
            default: "H1",
            depends_on: "eval:doc.period_type=='Half Year'"
        },

        // ---------------- YEAR ----------------
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: ["2023", "2024", "2025", "2026"],
            default: new Date().getFullYear().toString(),
            reqd: 1
        },

        // ---------------- REGION ----------------
        {
            fieldname: "custom_region",
            label: __("Region"),
            fieldtype: "Data"
        },

        // ---------------- LOCATION ----------------
        {
            fieldname: "custom_location",
            label: __("Location"),
            fieldtype: "Data"
        },

        // ---------------- TERRITORY ----------------
        {
            fieldname: "custom_territory_name",
            label: __("Territory"),
            fieldtype: "Data"
        },

        // ---------------- HEAD SALES PERSON ----------------
        {
            fieldname: "parent_sales_person",
            label: __("Head Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ---------------- CUSTOMER ----------------
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        }
    ],

    // Formatter for clickable invoice amounts
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "invoice_amount" && data && data.customer_name !== "TOTAL" && data.invoice_amount > 0) {
            value = `<a href="#" 
                        data-customer="${data.customer_name}" 
                        data-sales-person="${data.sales_person}"
                        data-from-date="${data.from_date}" 
                        data-to-date="${data.to_date}"
                        onclick="show_invoice_details(event, '${data.customer_name}', '${data.sales_person}', '${data.from_date}', '${data.to_date}')"
                        style="text-decoration: underline; color: #2490ef;">
                        ${value}
                    </a>`;
        }
        return value;
    },

    onload: function(report) {
        // Add custom CSS
        const style = document.createElement('style');
        style.innerHTML = `
            .invoice-details-dialog .modal-dialog {
                max-width: 80%;
            }
            .invoice-details-table {
                max-height: 400px;
                overflow-y: auto;
            }
            .invoice-details-table table {
                margin-bottom: 0;
            }
            .invoice-details-table tfoot {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            .invoice-link {
                color: #2490ef;
                text-decoration: none;
            }
            .invoice-link:hover {
                text-decoration: underline;
            }
        `;
        document.head.appendChild(style);

        // Define the click handler globally
        window.show_invoice_details = function(event, customer, sales_person, from_date, to_date) {
            event.preventDefault();
            
            // Create dialog
            const dialog = new frappe.ui.Dialog({
                title: __('Invoice Details - {0}', [customer]),
                size: 'large',
                fields: [
                    {
                        fieldtype: 'HTML',
                        fieldname: 'invoice_details',
                        options: '<div class="text-muted text-center">Loading...</div>'
                    }
                ],
                primary_action_label: __('Close'),
                primary_action: function() {
                    dialog.hide();
                }
            });
            
            dialog.show();
            
            // Fetch invoice details
            frappe.call({
                method: "vciplreportsv1001.vcipl1001.report.sales_person_report.sales_person_report.get_invoice_details",
                args: {
                    customer: customer,
                    sales_person: sales_person,
                    from_date: from_date,
                    to_date: to_date
                },
                callback: function(response) {
                    if (response.message && response.message.length > 0) {
                        let html = build_invoice_table(response.message);
                        dialog.fields_dict.invoice_details.$wrapper.html(html);
                    } else {
                        dialog.fields_dict.invoice_details.$wrapper.html(`
                            <div class="alert alert-warning text-center">
                                No invoices found for this period.
                            </div>
                        `);
                    }
                },
                error: function(r) {
                    dialog.fields_dict.invoice_details.$wrapper.html(`
                        <div class="alert alert-danger text-center">
                            Error loading invoice details: ${r.message}
                        </div>
                    `);
                }
            });
        };

        // Helper function to build invoice table
        function build_invoice_table(invoices) {
            if (!invoices || invoices.length === 0) {
                return '<div class="alert alert-info text-center">No invoices found</div>';
            }

            let total = 0;
            let rows = '';
            
            invoices.forEach(inv => {
                total += inv.amount;
                rows += `
                    <tr>
                        <td>
                            <a href="/app/sales-invoice/${inv.name}" 
                               target="_blank" 
                               class="invoice-link">
                                ${inv.name}
                            </a>
                        </td>
                        <td>${frappe.datetime.str_to_user(inv.posting_date)}</td>
                        <td>${inv.customer}</td>
                        <td class="text-right">${format_currency(inv.amount, inv.currency || 'INR')}</td>
                        <td>
                            <span class="indicator ${get_status_color(inv.status)}">
                                ${__(inv.status)}
                            </span>
                        </td>
                    </tr>
                `;
            });

            return `
                <div class="invoice-details-table">
                    <table class="table table-bordered table-hover">
                        <thead>
                            <tr>
                                <th>${__('Invoice No')}</th>
                                <th>${__('Posting Date')}</th>
                                <th>${__('Customer')}</th>
                                <th class="text-right">${__('Amount')}</th>
                                <th>${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                        <tfoot>
                            <tr>
                                <th colspan="3" class="text-right">${__('Total')}:</th>
                                <th class="text-right">${format_currency(total)}</th>
                                <th></th>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;
        }

        // Helper function for status colors
        function get_status_color(status) {
            const colors = {
                'Paid': 'green',
                'Unpaid': 'red',
                'Overdue': 'orange',
                'Draft': 'grey',
                'Return': 'blue',
                'Credit Note Issued': 'blue'
            };
            return colors[status] || 'grey';
        }

        // Helper function to format currency
        function format_currency(amount, currency = 'INR') {
            return frappe.format(amount, {fieldtype: 'Currency', currency: currency});
        }
    }
};
