frappe.query_reports["Monthwises Purchase"] = {

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
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
        }
    ],

    after_datatable_render: function (report) {

        $(".supplier-link").off("click").on("click", function (e) {
            e.preventDefault();

            const supplier = $(this).data("supplier");
            const filters = report.get_values();

            frappe.call({
                method: "vciplreportsv1001.vciplreportsv1001.vcipl1001.report.monthwises_purchase.monthwises_purchase.get_month_breakup",
                args: {
                    supplier: supplier,
                    supplier_group: filters.supplier_group,
                    month: filters.month
                },
                callback: function (r) {

                    const content = r.message.html + `
                        <div id="supplier_purchase_chart" style="margin-top:20px;"></div>
                    `;

                    frappe.msgprint({
                        title: "Month-wise Purchase - " + supplier,
                        message: content,
                        wide: true
                    });

                    setTimeout(() => {
                        new frappe.Chart("#supplier_purchase_chart", {
                            title: "Monthly Purchase Trend",
                            data: {
                                labels: r.message.labels,
                                datasets: [{
                                    name: "Purchase Amount",
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
