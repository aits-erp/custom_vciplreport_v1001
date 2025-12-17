frappe.query_reports["Sales Person Target Report"] = {

    filters: [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: [
                "2023",
                "2024",
                "2025"
            ],
            default: new Date().getFullYear().toString()
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // 🔹 Serial No clickable
        if (column.fieldname === "sr_no" && data) {
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

    onload: function (report) {

        report.datatable.on("click", function (e) {

            const cell = e.target.closest(".dt-cell");
            if (!cell) return;

            const colIndex = cell.dataset.colIndex;
            const rowIndex = cell.dataset.rowIndex;

            const column = report.datatable.datamanager.getColumn(colIndex);
            if (column.fieldname !== "sr_no") return;

            const rowData = report.datatable.datamanager.getRow(rowIndex);
            const sales_person = rowData.sales_person;

            if (!sales_person) {
                frappe.msgprint("Sales Person not found in this row");
                return;
            }

            // ✅ Correct ERPNext way
            frappe.route_options = {
                sales_person: sales_person,
                year: report.get_values().year
            };

            frappe.set_route(
                "query-report",
                "Customer Wise Sales Target Report"
            );
        });
    }
};
