frappe.query_reports["Customer Sales Target vs Achievement"] = {

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // 🔹 Serial No drill column
        if (column.fieldname === "sr_no") {
            return `
                <span class="sr-drill"
                      style="color:#1f6fd6; cursor:pointer; font-weight:600"
                      title="View Customer Wise Target">
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

            // Get clicked row index
            const row = $(this).closest(".dt-row");
            const rowIndex = row.attr("data-row-index");

            const rowData =
                frappe.query_report.datatable.datamanager.getRow(rowIndex);

            const sales_person = rowData.sales_person;

            if (!sales_person) {
                frappe.msgprint("Sales Person not found");
                return;
            }

            // 🔑 CORRECT WAY: set route_options BEFORE routing
            frappe.route_options = {
                sales_person: sales_person
            };

            frappe.set_route(
                "query-report",
                "Customer Wise Sales Target Report"
            );
        });
    }
};
