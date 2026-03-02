// Copyright (c) 2024, Your Organization and contributors
// For license information, please see license.txt

frappe.query_reports["Pricing Rule"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 100
        },
        {
            "fieldname": "custom_customer_name",
            "label": __("Custom Customer Name"),
            "fieldtype": "Data",
            "width": 150,
            "description": __("Search by custom customer name from Customer master")
        },
        {
            "fieldname": "from_date",
            "label": __("Valid From Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "to_date",
            "label": __("Valid Upto Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "valid_on_date",
            "label": __("Valid On Date"),
            "fieldtype": "Date",
            "width": 100,
            "description": __("Find rules valid on this specific date")
        },
        {
            "fieldname": "apply_on",
            "label": __("Apply On"),
            "fieldtype": "Select",
            "options": ["", "Item Code", "Item Group", "Brand", "Transaction"],
            "width": 100
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 100
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 100
        },
        {
            "fieldname": "selling",
            "label": __("Selling"),
            "fieldtype": "Check",
            "width": 80
        },
        {
            "fieldname": "buying",
            "label": __("Buying"),
            "fieldtype": "Check",
            "width": 80
        },
        {
            "fieldname": "disable",
            "label": __("Is Disabled"),
            "fieldtype": "Check",
            "width": 100
        },
        {
            "fieldname": "has_coupon",
            "label": __("Has Coupon Code"),
            "fieldtype": "Check",
            "width": 120
        },
        {
            "fieldname": "priority",
            "label": __("Priority"),
            "fieldtype": "Select",
            "options": ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
            "width": 100
        },
        {
            "fieldname": "tags",
            "label": __("Tags"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "search_text",
            "label": __("Search (ID/Title/Description)"),
            "fieldtype": "Data",
            "width": 150
        }
    ],
    
    "onload": function(report) {
        // Add clear filters button
        report.page.add_inner_button(__("Clear All Filters"), function() {
            report.filters.forEach(function(filter) {
                if (filter.df.fieldtype !== "Check") {
                    filter.set_input("");
                } else {
                    filter.set_input(0);
                }
            });
            report.refresh();
        });
        
        // Add today's date filter
        report.page.add_inner_button(__("Today's Valid Rules"), function() {
            var today = frappe.datetime.get_today();
            report.get_filter('valid_on_date').set_input(today);
            report.refresh();
        });
        
        // Add export button
        report.page.add_inner_button(__("Export as CSV"), function() {
            frappe.query_report.export_report();
        });
        
        // Show insights banner (matching your image)
        $(report.page.wrapper).find('.page-form').after(`
            <div class="alert alert-info alert-dismissible fade show" role="alert" style="margin: 10px 20px; background-color: #f0f7ff; border-color: #b8daff;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <strong><i class="fa fa-line-chart" style="margin-right: 8px;"></i>Get more insights with Frape Insights →</strong>
                        <span style="margin-left: 15px; color: #6c757d;">Analyze pricing trends and effectiveness</span>
                    </div>
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
            </div>
        `);
        
        // Add quick filter buttons for date ranges
        var date_filter_section = $(`
            <div class="row" style="margin: 10px 20px;">
                <div class="col-md-12">
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-default btn-sm date-quick-filter" data-days="7">Next 7 Days</button>
                        <button type="button" class="btn btn-default btn-sm date-quick-filter" data-days="15">Next 15 Days</button>
                        <button type="button" class="btn btn-default btn-sm date-quick-filter" data-days="30">Next 30 Days</button>
                        <button type="button" class="btn btn-default btn-sm date-quick-filter" data-past="1">Past 30 Days</button>
                        <button type="button" class="btn btn-default btn-sm date-quick-filter" data-past="2">Past 60 Days</button>
                    </div>
                </div>
            </div>
        `);
        
        $(report.page.wrapper).find('.page-form').after(date_filter_section);
        
        // Handle quick filter clicks
        $('.date-quick-filter').on('click', function() {
            var today = frappe.datetime.get_today();
            var days = $(this).data('days');
            var past = $(this).data('past');
            
            if (days) {
                var future_date = frappe.datetime.add_days(today, parseInt(days));
                report.get_filter('from_date').set_input(today);
                report.get_filter('to_date').set_input(future_date);
            } else if (past) {
                var past_date = frappe.datetime.add_days(today, -parseInt(past));
                report.get_filter('from_date').set_input(past_date);
                report.get_filter('to_date').set_input(today);
            }
            
            report.refresh();
        });
    },
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Highlight expired pricing rules
        if (column.fieldname === "valid_upto" && data.valid_upto) {
            var today = frappe.datetime.get_today();
            if (data.valid_upto < today) {
                value = `<span style="color: #dc3545; font-weight: bold;">${value} (Expired)</span>`;
            }
        }
        
        // Highlight future rules
        if (column.fieldname === "valid_from" && data.valid_from) {
            var today = frappe.datetime.get_today();
            if (data.valid_from > today) {
                value = `<span style="color: #28a745; font-weight: bold;">${value} (Future)</span>`;
            }
        }
        
        // Highlight disabled rules
        if (column.fieldname === "disable" && data.disable == 1) {
            value = `<span style="color: #6c757d;">Disabled</span>`;
        }
        
        // Highlight rules with coupons
        if (column.fieldname === "coupon_code" && data.coupon_code) {
            value = `<span style="color: #fd7e14; font-weight: bold;">${value}</span>`;
        }
        
        // Format rate and discount
        if (column.fieldname === "rate" && data.rate) {
            if (data.currency) {
                value = frappe.format(data.rate, {fieldtype: "Currency", currency: data.currency});
            }
        }
        
        return value;
    },
    
    "tree": false,
    "name_field": "name",
    "parent_field": "parent_pricing_rule",
    "initial_depth": 0,
    
    "after_refresh": function(report) {
        // Add summary statistics
        var data = report.data;
        if (data && data.length > 0) {
            var total_rules = data.length;
            var active_rules = data.filter(d => !d.disable).length;
            var expired_rules = data.filter(d => d.valid_upto && d.valid_upto < frappe.datetime.get_today()).length;
            var future_rules = data.filter(d => d.valid_from && d.valid_from > frappe.datetime.get_today()).length;
            
            var stats_html = `
                <div class="row" style="margin: 10px 20px;">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body" style="padding: 10px;">
                                <span class="badge badge-primary" style="margin-right: 10px;">Total: ${total_rules}</span>
                                <span class="badge badge-success" style="margin-right: 10px;">Active: ${active_rules}</span>
                                <span class="badge badge-danger" style="margin-right: 10px;">Expired: ${expired_rules}</span>
                                <span class="badge badge-warning" style="margin-right: 10px;">Future: ${future_rules}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (!report.$summary_stats) {
                report.$summary_stats = $(stats_html).insertAfter(report.page.wrapper.find('.page-form'));
            } else {
                report.$summary_stats.html(stats_html);
            }
        }
    }
};
