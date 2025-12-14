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

    after_datatable_render: function (report) {

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
                        <div id="customer_sales_chart" style="margin-top:20px;"></div>
                    `;

                    frappe.msgprint({
                        title: "Month-wise Sales - " + customer,
                        message: content,
                        wide: true
                    });

                    setTimeout(() => {
                        new frappe.Chart("#customer_sales_chart", {
                            title: "Monthly Sales Trend",
                            data: {
                                labels: r.message.labels,
                                datasets: [{
                                    name: "Sales",
                                    type: "bar",
                                    values: r.message.values
                                }]
                            },
                            type: "bar",
                            height: 300
                        });
                    }, 300);
                }
            });
        });
    }
};
