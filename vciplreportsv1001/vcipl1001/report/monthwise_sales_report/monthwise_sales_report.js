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
    }
};


// ✅ EVENT DELEGATION (IMPORTANT FIX)
$(document).on("click", ".month-amount", function (e) {
    e.preventDefault();

    const customer = $(this).data("customer");
    const month = frappe.query_report.get_filter_value("month");
    const customer_group = frappe.query_report.get_filter_value("customer_group");

    frappe.call({
        method: "vciplreports_v01.vciplreports_v01.vcipl.report.monthwise_sales_report.monthwise_sales_report.get_invoice_drilldown",
        args: {
            customer: customer,
            month: month,
            customer_group: customer_group
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


// ------------------------------
// MAIN BAR CHART
// ------------------------------
function render_main_bar_chart(report) {

    if (!report.data || !report.data.length) return;

    let total = report.data.reduce((sum, r) => sum + flt(r.month_amount_raw || 0), 0);

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
