frappe.router.on("change", () => {
    const route = frappe.get_route();
    if (route[0] === "query-report" && route[1] === "Sales Analytic Dashboard") {
        let tries = 0;
        const timer = setInterval(() => {
            tries++;
            const qr = frappe.query_report;
            const f = qr && qr.report_name === "Sales Analytic Dashboard"
                && qr.get_filter && qr.get_filter("to_date");
            if (f) {
                clearInterval(timer);
                f.set_value(frappe.datetime.get_today());
            } else if (tries > 40) {
                clearInterval(timer);
            }
        }, 300);
    }
});