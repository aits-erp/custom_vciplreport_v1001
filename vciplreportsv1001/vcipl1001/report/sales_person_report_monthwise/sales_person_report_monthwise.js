frappe.query_reports["Sales Person Report Monthwise"] = {

    filters: [
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: ["2023", "2024", "2025"],
            default: new Date().getFullYear().toString()
        },
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: [
                { label: "January", value: 1 },
                { label: "February", value: 2 },
                { label: "March", value: 3 },
                { label: "April", value: 4 },
                { label: "May", value: 5 },
                { label: "June", value: 6 },
                { label: "July", value: 7 },
                { label: "August", value: 8 },
                { label: "September", value: 9 },
                { label: "October", value: 10 },
                { label: "November", value: 11 },
                { label: "December", value: 12 },
            ],
            default: new Date().getMonth() + 1
        },
        {
            fieldname: "main_group",
            label: "Main Group",
            fieldtype: "Data"
        },
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "sales_person",
            label: "Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // 🔥 ACHIEVED DRILLDOWN
        if (column.fieldname === "achieved" && data.achieved > 0) {

            const f = frappe.query_report.get_values();

            return `
                <a href="/app/sales-invoice?
                customer=${data.customer}
                &sales_person=${data.sales_person}
                &from_date=${f.year}-${String(f.month).padStart(2, '0')}-01
                &to_date=${f.year}-${String(f.month).padStart(2, '0')}-31"
                target="_blank">
                ${value}
                </a>
            `;
        }

        return value;
    }
};
