// report_dashboard.js
frappe.pages['report-dashboard'].on_page_load = function (wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Report Dashboard',
        single_column: true
    });

    // Render HTML template
    $(frappe.render_template("report_dashboard", {})).appendTo(page.body);

    // Central report path mapping
    const REPORT_PATHS = {
        "Distributor Report": "/app/query-report/Distributors%20Report",
        "Top selling below MSL report": "/app/query-report/Most%20Selling%20Below%20MSL%20Report?custom_item_type=Finished+Goods",
        "Top Most Selling Items": "/app/query-report/Top%20Most%20Selling%20Items",
        "Bottom 100 Most selling Item": "/app/query-report/Bottom%20100%20Most%20selling%20Item",
        "Outstanding Debtors Monthwise": "/app/query-report/Outstanding%20Debtors%20Monthwise",
        "Sales Person Report": "/app/query-report/Sales%20Person%20-%20Report?month=1&year=2026",
        "Sales Analytics Report": "/app/query-report/Sales%20Analytics%20Report",
        "Monthwise Sales Report": "/app/query-report/Monthwise%20Sales%20Report",
        "Sales order - with available qtyss": "/app/sales-order/view/report/Sales%20order%20-%20with%20available%20qtyss",
        "Monthwises Purchase": "/app/query-report/Monthwises%20Purchase",
        "Item Category Wise - Report": "/app/query-report/Item%20Category%20Wise%20-%20Report"
    };

    // Click handler
    page.body.on("click", ".report-card", function () {

        let report_name = $(this).data("report");
        if (!report_name) return;

        // click animation
        $(this).css("transform", "scale(0.96)");

        setTimeout(() => {
            $(this).css("transform", "");

            // Navigate safely
            if (REPORT_PATHS[report_name]) {
                window.location.href = REPORT_PATHS[report_name];
            } else {
                frappe.msgprint({
                    title: "Report Not Configured",
                    message: `No route defined for <b>${report_name}</b>`,
                    indicator: "orange"
                });
            }

        }, 140);
    });
};
