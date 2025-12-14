frappe.query_reports["Monthwise Purchases"] = {

    filters: [
        {
            fieldname: "supplier_group",
            label: "Supplier Group",
            fieldtype: "Link",
            options: "Supplier Group"
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

        $(".supplier-link").off("click").on("click", function (e) {
            e.preventDefault();

            let supplier = $(this).data("supplier");
            let filters = report.get_values();

            frappe.call({
                method: "vciplreports_v01.vciplreports_v01.vcipl.report.monthwise_purchases.monthwise_purchases.get_month_breakup",
                args: {
                    supplier: supplier,
                    supplier_group: filters.supplier_group,
                    month: filters.month
                },
                callback: function (r) {

                    let content = r.message.html + `
                        <div id="supplier_purchase_chart" style="margin-top:20px;"></div>
                    `;

                    frappe.msgprint({
                        title: "Month-wise Purchases - " + supplier,
                        message: content,
                        wide: true
                    });

                    setTimeout(() => {
                        new frappe.Chart("#supplier_purchase_chart", {
                            title: "Purchase Trend",
                            data: {
                                labels: r.message.labels,
                                datasets: [{
                                    name: "Purchase",
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
