frappe.query_reports["Sales Person Target Report"] = {

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "sr_no") {
            return `<span class="sr-drill"
                        style="color:#1f6fd6; cursor:pointer; font-weight:600">
                        ${value}</span>`;
        }
        return value;
    },

    onload: function (report) {
        report.datatable.on("click", function (e) {

            const cell = e.target.closest(".dt-cell");
            if (!cell) return;

            const col = report.datatable.datamanager.getColumn(cell.dataset.colIndex);
            if (col.fieldname !== "sr_no") return;

            const row = report.datatable.datamanager.getRow(cell.dataset.rowIndex);

            frappe.route_options = {
                sales_person: row.sales_person
            };

            frappe.set_route(
                "query-report",
                "Customer Wise Sales Target Report"
            );
        });
    }
};
