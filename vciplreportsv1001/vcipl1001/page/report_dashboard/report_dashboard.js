// report_dashboard.js
frappe.pages['report-dashboard'].on_page_load = function (wrapper) {

    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Report Dashboard',
        single_column: true
    });

    // Render HTML
    $(frappe.render_template("report_dashboard", {}))
        .appendTo(page.body);

    // ================================
    // CENTRAL REPORT ROUTE CONFIG
    // ================================
    const REPORT_PATHS = {
        "Outstanding Debtors Report":
            "/app/query-report/Outstanding%20Debtors%20Report?customer_group=Debtors+Distributors",

        "Top selling below MSL report":
            "/app/query-report/Most%20Selling%20Below%20MSL%20Report?custom_item_type=Finished+Goods",

        "Top Most Selling Items":
            "/app/query-report/Top%20Most%20Selling%20Items",

        "Bottom 100 Most selling Item":
            "/app/query-report/Bottom%20100%20Most%20selling%20Item",

        "Sales Person Report":
            "/app/query-report/Sales%20Person%20Report?month=1&year=2026",

        "Monthwise Sales Report":
            "/app/query-report/Monthwise%20Sales%20Report",

        "Pending Sales Order Report":
            "/app/query-report/Pending%20Sales%20Order%20Report" +
            "?company=Vinod+Cookware+India+Private+Limited&group_by_so=1",

        "Monthwises Purchase":
            "/app/query-report/Monthwises%20Purchase",

        "Item Category Wise - Report":
            "/app/query-report/Item%20Category%20Wise%20-%20Report",

        "Stock Balance Report":
            "/app/query-report/Stock%20Report%20-%20Cumulative",

        "Pricing Rule Report":
            "/app/query-report/Pricing%20Rule%20Report",
            
        "Accounts Receivable":"/app/query-report/Accounts%20Receivable?company=Vinod+Cookware+India+Private+Limited&report_date=2026-01-30&ageing_based_on=Due+Date&calculate_ageing_with=Report+Date&range=30%2C+60%2C+90%2C+120"
        


           
    };

    // ================================
    // CARD CLICK HANDLER
    // ================================
    $(page.body).on("click", ".report-card", function () {

        const report_name = $(this).data("report");
        if (!report_name) return;

        // click animation
        const card = $(this);
        card.css("transform", "scale(0.96)");

        setTimeout(() => {
            card.css("transform", "");

            if (REPORT_PATHS[report_name]) {
                // ERPNext-safe navigation
                window.location.href = REPORT_PATHS[report_name];
            } else {
                frappe.msgprint({
                    title: __("Report Not Configured"),
                    message: __("No route defined for <b>{0}</b>", [report_name]),
                    indicator: "orange"
                });
            }

        }, 140);
    });
};
