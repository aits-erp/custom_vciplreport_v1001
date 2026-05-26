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

        // "TSO WISE CATEGORYWISE":
        //     "/app/query-report/TSO%20WISE%20CATEGORYWISE1?from_date=2026-05-01&to_date=2026-05-31&customer_group=Debtors+Distributors&custom_main_group=%5B"Assorted+Utensils"%2C"Bag"%2C"Bottle"%2C"Carton"%2C"Cast+Iron"%2C"Circle"%2C"Coil"%2C"Csd"%2C"Electrical+Appliances"%2C"Futuretec"%2C"Healux"%2C"Horeca"%2C"Kraft"%2C"Machinery"%2C"Nonstick"%2C"Other"%2C"Other+Spare"%2C"Platinum"%2C"Platinum+Triply+P.cooker"%2C"Polishing"%2C"Powder"%2C"Pressure+Cookers"%2C"SFG"%2C"SS+Cookware"%2C"Scrap"%2C"Sticker+%26+Warranty+Card"%2C"Tool"%2C"Trading+SFG"%5D",
        "TSO WISE CATEGORYWISE":
    "/app/query-report/TSO%20WISE%20CATEGORYWISE1?from_date=2026-05-01&to_date=2026-05-31&customer_group=Debtors+Distributors&custom_main_group=%5B%22Assorted+Utensils%22%2C%22Bag%22%2C%22Bottle%22%2C%22Carton%22%2C%22Cast+Iron%22%2C%22Circle%22%2C%22Coil%22%2C%22Csd%22%2C%22Electrical+Appliances%22%2C%22Futuretec%22%2C%22Healux%22%2C%22Horeca%22%2C%22Kraft%22%2C%22Machinery%22%2C%22Nonstick%22%2C%22Other%22%2C%22Other+Spare%22%2C%22Platinum%22%2C%22Platinum+Triply+P.cooker%22%2C%22Polishing%22%2C%22Powder%22%2C%22Pressure+Cookers%22%2C%22SFG%22%2C%22SS+Cookware%22%2C%22Scrap%22%2C%22Sticker+%26+Warranty+Card%22%2C%22Tool%22%2C%22Trading+SFG%22%5D",

        "Monthwise Sales Report":
            "/app/query-report/Monthwise%20Sales%20Report",

        "Pending Sales Order Report":
            "/app/query-report/Pending%20Sales%20Order%20Report" +
            "?company=Vinod+Cookware+India+Private+Limited&group_by_so=1",

        "FILL RATIO SALES ORDER":
            "/app/query-report/FILL%20RATIO%20SALES%20ORDER?company=AITS+%28Demo%29",

        "Customer Fill Ratio":
            "/app/query-report/Customer%20Fill%20Ratio?company=AITS+%28Demo%29",

            "Supplier Fill Ratio":
            "/app/query-report/Supplier%20Fill%20Ratio?company=AITS+%28Demo%29",

        "Monthwises Purchase":
            "/app/query-report/Monthwises%20Purchase",

        "Item Category Wise - Report":
            "/app/query-report/Item%20Category%20Wise%20-%20Report",

        "Stock Balance Report":
            "/app/query-report/Stock%20Report%20-%20Cumulative",

        "Pricing Rule Report":
            "/app/query-report/Pricing%20Rule",

        "Item Category Wise - Report": "/app/query-report/Item%20Category%20Wise%20-%20Report?from_date=2026-01-01&to_date=2026-01-31",   
            
        "Ageing Report - Customers":"/app/query-report/Ageing%20Report%20-%20Customers"
        
       
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
