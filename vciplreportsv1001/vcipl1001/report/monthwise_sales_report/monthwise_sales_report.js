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
            options: [
                "",
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
        }
    ],

    // ===============================
    // AFTER TABLE LOAD
    // ===============================
    after_datatable_render: function (report) {

        // 🔥 MAIN BAR CHART (like Accounts Receivable)
        render_main_bar_chart(report);

        // ===============================
        // CUSTOMER CLICK POPUP
        // ===============================
        $(".customer-link").off("click").on("click", function (e) {
            e.preventDefault();

            let customer = $(this).data("customer");
            let filters = report.get_values();

            frappe.call({
                method: "vciplreports_v01.vciplreports_v01.vcipl.report.monthwise_sales_report.monthwise_sales_report.get_month_breakup",
                args: {
                    customer: customer,
                    customer_group: filters.customer_group,
                    month: filters.month
                },
                callback: function (r) {

                    let content = r.message.html + `
                        <div id="customer_bar_chart" style="margin-top:20px;"></div>
                        <div id="customer_pie_chart" style="margin-top:20px;"></div>
                    `;

                    frappe.msgprint({
                        title: "Month-wise Sales - " + customer,
                        message: content,
                        wide: true
                    });

                    setTimeout(() => {

                        // BAR CHART (Popup)
                        new frappe.Chart("#customer_bar_chart", {
                            title: "Monthly Sales Trend",
                            data: {
                                labels: r.message.labels,
                                datasets: [{
                                    name: "Sales",
                                    values: r.message.values
                                }]
                            },
                            type: "bar",
                            height: 260
                        });

                        // PIE CHART (Popup)
                        new frappe.Chart("#customer_pie_chart", {
                            title: "Sales Distribution",
                            data: {
                                labels: r.message.labels,
                                datasets: [{
                                    values: r.message.values
                                }]
                            },
                            type: "pie",
                            height: 240
                        });

                    }, 300);
                }
            });
        });
    }
};


// ==================================================
// MAIN REPORT BAR CHART (NATIVE ERPNext STYLE)
// ==================================================
function render_main_bar_chart(report) {

    if (!report.data || report.data.length === 0) return;

    const month_keys = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ];

    const month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ];

    let totals = Array(12).fill(0);

    report.data.forEach(row => {
        month_keys.forEach((key, idx) => {
            totals[idx] += flt(row[key] || 0);
        });
    });

    let labels = [];
    let values = [];

    totals.forEach((val, idx) => {
        if (val > 0) {
            labels.push(month_labels[idx]);
            values.push(val);
        }
    });

    // 🔥 Native ERPNext chart (same behavior as Accounts Receivable)
    report.chart = {
        data: {
            labels: labels,
            datasets: [
                {
                    name: "Total Sales",
                    values: values
                }
            ]
        },
        type: "bar",   // ✅ BAR chart
        height: 250
    };
}
