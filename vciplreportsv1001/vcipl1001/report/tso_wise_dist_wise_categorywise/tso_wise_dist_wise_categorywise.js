frappe.query_reports["TSO WISE DIST WISE CATEGORYWISE"] = {

    filters: [

        {
            fieldname: "period_type",
            label: "Period Type",
            fieldtype: "Select",
            options: ["Date Range", "Quarter", "Half Year", "Year"],
            default: "Date Range"
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            depends_on: "eval:doc.period_type=='Date Range'"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            depends_on: "eval:doc.period_type=='Date Range'"
        },

        {
            fieldname: "quarter",
            label: "Quarter",
            fieldtype: "Select",
            options: ["Q1","Q2","Q3","Q4"],
            depends_on: "eval:doc.period_type=='Quarter'"
        },

        {
            fieldname: "half_year",
            label: "Half Year",
            fieldtype: "Select",
            options: ["H1","H2"],
            depends_on: "eval:doc.period_type=='Half Year'"
        },

        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: ["2023","2024","2025","2026"],
            default: new Date().getFullYear().toString(),
            reqd: 1
        },

        {
            fieldname: "tso",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person"
        },

        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },

        {
            fieldname: "region",
            label: "Sales Region",
            fieldtype: "Data"
        },

        {
            fieldname: "territory",
            label: "Sales Territory",
            fieldtype: "Data"
        },

        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },

        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group",
            default: "Debtors Distributors"
        },

        {
            fieldname: "main_group",
            label: "Category",
            fieldtype: "Data"
        },

        {
            fieldname: "include_customer_sub_group",
            label: "Include Customer Sub Group",
            fieldtype: "Check",
            default: 0
        },

        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        }
    ]
};