frappe.query_reports["Monthwises Purchase"] = {

    filters: [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Int",
            default: new Date().getFullYear()
        }
    ],

    after_datatable_render: function (report) {

        $(".supplier-link").off("click").on("click", function (e) {
            e.preventDefault();

            let supplier = $(this).data("supplier");
            let filters = report.get_values();

            frappe.call({
                method: "vciplreports_v01.vciplreports_v01.vcipl.report.monthwise_purchases.monthwise_purchases.get_month_breakup",
                args: {
                    supplier: supplier,
                    company: filters.company,
                    year: filters.year
                },
                callback: function (r) {

                    // Add chart container
                    let content = r.message.html + `
                        <div id="supplier_purchase_chart" style="margin-top:20px;"></div>
                    `;

                    frappe.msgprint({
                        title: "Month-wise Purchases - " + supplier,
                        message: content,
                        wide: true
                    });

                    // Render Chart
                    setTimeout(() => {
                        new frappe.Chart("#supplier_purchase_chart", {
                            title: "Monthly Purchase Trend",
                            data: {
                                labels: r.message.labels,
                                datasets: [
                                    {
                                        name: "Purchase",
                                        type: "bar",
                                        values: r.message.values
                                    }
                                ]
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
