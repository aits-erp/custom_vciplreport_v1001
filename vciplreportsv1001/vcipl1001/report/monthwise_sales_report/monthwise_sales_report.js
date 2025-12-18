frappe.query_reports["Monthwise Sales Report"] = {

    filters: [
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group"
        },
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            reqd: 1,
            options: [
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ]
        }
    ],

    after_datatable_render: function (report) {

        render_main_bar_chart(report);

        // ------------------------------
        // CLICK ON AMOUNT → DRILLDOWN
        // ------------------------------
        $(".month-amount").off("click").on("click", function (e) {
            e.preventDefault();

            const customer = $(this).data("customer");
            const month = report.get_values().month;

            frappe.call({
                method: "vciplreports_v01.vciplreports_v01.vcipl.report.monthwise_sales_report.monthwise_sales_report.get_invoice_drilldown",
                args: {
                    customer: customer,
                    month: month
                },
                callback: function (r) {
                    frappe.msgprint({
                        title: `Sales Invoices - ${customer} (${month})`,
                        message: r.message,
                        wide: true
                    });
                }
            });
        });
    }
};


// ----------------------------------
// MAIN BAR CHART
// ----------------------------------
function render_main_bar_chart(report) {

    if (!report.data || report.data.length === 0) return;

    let total = 0;

    report.data.forEach(r => {
        total += flt(r.month_amount || 0);
    });

    report.chart = {
        data: {
            labels: [report.get_values().month],
            datasets: [{
                name: "Total Sales",
                values: [total]
            }]
        },
        type: "bar",
        height: 250
    };
}
