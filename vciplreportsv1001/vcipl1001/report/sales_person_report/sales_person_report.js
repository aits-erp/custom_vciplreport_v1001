frappe.query_reports["Sales Person Report"] = {
    filters: [
        // ---------------- PERIOD TYPE ----------------
        {
            fieldname: "period_type",
            label: "Period Type",
            fieldtype: "Select",
            options: ["Month", "Quarter", "Half Year"],
            default: "Month",
            reqd: 1
        },

        // ---------------- MONTH ----------------
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

        // ---------------- QUARTER (FY STYLE) ----------------
        {
            fieldname: "quarter",
            label: "Quarter",
            fieldtype: "Select",
            options: [
                { label: "Q1 (Apr–Jun)", value: "Q1" },
                { label: "Q2 (Jul–Sep)", value: "Q2" },
                { label: "Q3 (Oct–Dec)", value: "Q3" },
                { label: "Q4 (Jan–Mar)", value: "Q4" }
            ],
            default: "Q1",
            depends_on: "eval:doc.period_type=='Quarter'"
        },

        // ---------------- HALF YEAR ----------------
        {
            fieldname: "half_year",
            label: "Half Year",
            fieldtype: "Select",
            options: [
                { label: "H1 (Apr–Sep)", value: "H1" },
                { label: "H2 (Oct–Mar)", value: "H2" }
            ],
            default: "H1",
            depends_on: "eval:doc.period_type=='Half Year'"
        },

        // ---------------- YEAR ----------------
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: ["2023", "2024", "2025", "2026"],
            default: new Date().getFullYear().toString(),
            reqd: 1
        },

        // ---------------- REGION ----------------
        {
            fieldname: "custom_region",
            label: "Region",
            fieldtype: "Data"
        },

        // ---------------- LOCATION ----------------
        {
            fieldname: "custom_location",
            label: "Location",
            fieldtype: "Data"
        },

        // ---------------- TERRITORY (updated fieldname) ----------------
        {
            fieldname: "custom_territory_name",
            label: "Territory",
            fieldtype: "Data"
        },

        // ---------------- HEAD SALES PERSON ----------------
        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ---------------- CUSTOMER ----------------
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        }
    ]
};
