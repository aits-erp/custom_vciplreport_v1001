frappe.query_reports["Sales Person Report"] = {
    filters: [
        {
            fieldname: "period_type",
            label: "Period Type",
            fieldtype: "Select",
            options: ["Month", "Quarter", "Half Year"],
            default: "Month",
            reqd: 1
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
                { label: "December", value: 12 }
            ],
            default: new Date().getMonth() + 1,
            depends_on: "eval:doc.period_type=='Month'"
        },
        {
            fieldname: "quarter",
            label: "Quarter",
            fieldtype: "Select",
            options: [
                { label: "Q1 (Jan–Mar)", value: "Q1" },
                { label: "Q2 (Apr–Jun)", value: "Q2" },
                { label: "Q3 (Jul–Sep)", value: "Q3" },
                { label: "Q4 (Oct–Dec)", value: "Q4" }
            ],
            depends_on: "eval:doc.period_type=='Quarter'"
        },
        {
            fieldname: "half_year",
            label: "Half Year",
            fieldtype: "Select",
            options: [
                { label: "H1 (Jan–Jun)", value: "H1" },
                { label: "H2 (Jul–Dec)", value: "H2" }
            ],
            depends_on: "eval:doc.period_type=='Half Year'"
        },
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: ["2023", "2024", "2025", "2026"],
            default: new Date().getFullYear().toString(),
            reqd: 1
        },
        {
            fieldname: "custom_territory",
            label: "Territory",
            fieldtype: "Data"
        },
        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        }
    ]
};
