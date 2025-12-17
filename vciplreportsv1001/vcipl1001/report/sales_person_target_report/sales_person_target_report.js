frappe.query_reports["Customer Sales Target vs Achievement"] = {

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "sr_no") {
            return `
                <span class="sr-drill"
                      style="color:#1f6fd6; cursor:pointer; font-weight:600"
                      data-sales-person="${data.sales_person}">
                      ${value}
                </span>
            `;
        }

        return value;
    },

    onload: function () {

        $(document).on("click", ".sr-drill", function (e) {
            e.preventDefault();
            e.stopPropagation();

            const sales_person = $(this).data("sales-person");

            // 🔥 Open customer-wise report
            frappe.set_route("query-report", "Customer Wise Sales Target Report", {
                sales_person: sales_person
            });
        });
    }
};
