// Copyright (c) 2024, Your Organization and contributors
// For license information, please see license.txt

frappe.query_reports["Pricing Rule"] = {
    "filters": [
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
            "fieldname": "active_on_date",
            "label": __("Active On Date"),
            "fieldtype": "Date",
            "width": 100,
            "description": __("Show rules active on this specific date")
        }
    ],
    
    "onload": function(report) {
        // Clear Filters button
        report.page.add_inner_button(__("Clear Filters"), function() {
            report.filters.forEach(function(filter) {
                filter.set_input("");
            });
            report.refresh();
        });
        
        // Today's Active Rules button
        report.page.add_inner_button(__("Today's Active Rules"), function() {
            var today = frappe.datetime.get_today();
            report.get_filter('active_on_date').set_input(today);
            report.refresh();
        });
        
        // Export button
        report.page.add_inner_button(__("Export CSV"), function() {
            frappe.query_report.export_report();
        });
        
        // Print button
        report.page.add_inner_button(__("Print"), function() {
            frappe.query_report.print_report();
        });
        
        // Quick date filters
        var quick_filters = $(`
            <div class="row" style="margin: 10px 20px;">
                <div class="col-md-12">
                    <div class="btn-group" role="group" style="flex-wrap: wrap; gap: 5px;">
                        <button type="button" class="btn btn-sm btn-outline-primary date-quick-filter" data-action="today">Today</button>
                        <button type="button" class="btn btn-sm btn-outline-primary date-quick-filter" data-action="this_week">This Week</button>
                        <button type="button" class="btn btn-sm btn-outline-primary date-quick-filter" data-action="this_month">This Month</button>
                        <button type="button" class="btn btn-sm btn-outline-primary date-quick-filter" data-action="next_7">Next 7 Days</button>
                        <button type="button" class="btn btn-sm btn-outline-primary date-quick-filter" data-action="next_30">Next 30 Days</button>
                        <button type="button" class="btn btn-sm btn-outline-primary date-quick-filter" data-action="expired">Expired</button>
                    </div>
                </div>
            </div>
        `).insertAfter(report.page.wrapper.find('.page-form'));
        
        // Handle quick filter clicks
        quick_filters.find('.date-quick-filter').on('click', function() {
            var action = $(this).data('action');
            var today = frappe.datetime.get_today();
            
            report.get_filter('from_date').set_input("");
            report.get_filter('to_date').set_input("");
            report.get_filter('active_on_date').set_input("");
            
            switch(action) {
                case 'today':
                    report.get_filter('active_on_date').set_input(today);
                    break;
                case 'this_week':
                    var week_start = frappe.datetime.week_start();
                    var week_end = frappe.datetime.week_end();
                    report.get_filter('from_date').set_input(week_start);
                    report.get_filter('to_date').set_input(week_end);
                    break;
                case 'this_month':
                    var month_start = frappe.datetime.month_start();
                    var month_end = frappe.datetime.month_end();
                    report.get_filter('from_date').set_input(month_start);
                    report.get_filter('to_date').set_input(month_end);
                    break;
                case 'next_7':
                    report.get_filter('from_date').set_input(today);
                    report.get_filter('to_date').set_input(frappe.datetime.add_days(today, 7));
                    break;
                case 'next_30':
                    report.get_filter('from_date').set_input(today);
                    report.get_filter('to_date').set_input(frappe.datetime.add_days(today, 30));
                    break;
                case 'expired':
                    report.get_filter('to_date').set_input(frappe.datetime.add_days(today, -1));
                    break;
            }
            
            report.refresh();
        });
    },
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        var today = frappe.datetime.get_today();
        
        // Color code based on validity
        if (column.fieldname === "valid_upto" && data.valid_upto) {
            if (data.valid_upto < today) {
                value = `<span style="color: #dc3545; font-weight: bold;">${value} (Expired)</span>`;
            }
        }
        
        if (column.fieldname === "valid_from" && data.valid_from) {
            if (data.valid_from > today) {
                value = `<span style="color: #28a745; font-weight: bold;">${value} (Future)</span>`;
            }
        }
        
        // Highlight disabled rules
        if (column.fieldname === "disable" && data.disable == 1) {
            value = `<span style="color: #6c757d;">Disabled</span>`;
        }
        
        return value;
    },
    
    "after_refresh": function(report) {
        var data = report.data;
        
        if (data && data.length > 0) {
            var today = frappe.datetime.get_today();
            
            var total = data.length;
            var active = data.filter(d => !d.disable && 
                (!d.valid_upto || d.valid_upto >= today) &&
                (!d.valid_from || d.valid_from <= today)
            ).length;
            var expired = data.filter(d => d.valid_upto && d.valid_upto < today).length;
            var future = data.filter(d => d.valid_from && d.valid_from > today).length;
            var disabled = data.filter(d => d.disable == 1).length;
            
            var stats_html = `
                <div class="row" style="margin: 10px 20px;">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body py-2 px-3" style="background: #f8f9fa;">
                                <span class="badge badge-secondary mr-2 p-2">Total: ${total}</span>
                                <span class="badge badge-success mr-2 p-2">Active: ${active}</span>
                                <span class="badge badge-danger mr-2 p-2">Expired: ${expired}</span>
                                <span class="badge badge-warning mr-2 p-2">Future: ${future}</span>
                                <span class="badge badge-dark mr-2 p-2">Disabled: ${disabled}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (!report.$stats) {
                report.$stats = $(stats_html).insertAfter(report.page.wrapper.find('.page-form'));
            } else {
                report.$stats.html($(stats_html).html());
            }
        }
    }
};
