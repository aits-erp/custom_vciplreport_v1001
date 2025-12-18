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
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // 🔹 Click Achieved → Open Invoice List
        if (column.fieldname === "achieved" && data.achieved > 0) {
            const filters = frappe.query_report.get_values();

            return `
                <a href="/app/sales-invoice?
                sales_person=${data.sales_person}
                &from_date=${filters.year}-${filters.month}-01
                &to_date=${filters.year}-${filters.month}-31"
                target="_blank">
                ${value}
                </a>
            `;
        }

        return value;
    }
};
