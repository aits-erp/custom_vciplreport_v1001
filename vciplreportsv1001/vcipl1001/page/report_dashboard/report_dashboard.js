// report_dashboard.js
frappe.pages['report-dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Report Dashboard',
        single_column: true
    });

    $(frappe.render_template("report_dashboard", {})).appendTo(page.body);

    // Click handler for cards
    page.body.on("click", ".report-card", function () {
        let report_name = $(this).data("report");
        if (!report_name) return;

        // small click animation
        $(this).css("transform","scale(0.96)");
        setTimeout(() => {
            $(this).css("transform","");
            // navigate to query report; if it's a script report or query report, same route works
            frappe.set_route("query-report", report_name);
        }, 140);
    });
};
