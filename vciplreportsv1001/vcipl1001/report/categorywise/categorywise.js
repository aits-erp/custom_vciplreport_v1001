frappe.query_reports["CATEGORYWISE"] = {

    filters: [

        // ================= PERIOD TYPE =================
        {
            fieldname: "period_type",
            label: "Period Type",
            fieldtype: "Select",
            options: ["Date Range", "Quarter", "Half Year", "Year"],
            default: "Date Range"
        },

        // ---------------- DATE ----------------
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

        // ---------------- QUARTER ----------------
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

        // ================= EXISTING FILTERS =================

        {
            fieldname: "tso",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person",
            get_query: function () {
                return { filters: { is_group: 0 } };
            }
        },

        {
            fieldname: "parent_sales_person",
            label: "Parent Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },

        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },

        // 🔥 NEW CUSTOMER GROUP FILTER
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group",
            default: "Debtors Distributors"
        },

        {
            fieldname: "item_group",
            label: "Category",
            fieldtype: "Link",
            options: "Item Group"
        },

        {
            fieldname: "main_group",
            label: "Main Group",
            fieldtype: "Data"
        },

        {
            fieldname: "item",
            label: "Item",
            fieldtype: "Link",
            options: "Item"
        },

        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Warehouse"
        },

        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        },

        // ================= TOGGLES =================

        {
            fieldname: "show_customer_group",
            label: "Show Customer Group",
            fieldtype: "Check",
            default: 0
        },

        {
            fieldname: "show_category",
            label: "Show Category",
            fieldtype: "Check",
            default: 0
        },

        {
            fieldname: "show_item",
            label: "Show Item",
            fieldtype: "Check",
            default: 0
        }

    ],

    // ================= DRILL DOWN =================
    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        // 🔥 Click on amount → open invoice list
        if (column.fieldname === "amount" && data && data.customer_name) {
            return `<a href="#" onclick="open_invoice('${data.customer_name}')">${value}</a>`;
        }

        return value;
    }
};


// 🔥 Drill function
function open_invoice(customer_name) {
    frappe.set_route("List", "Sales Invoice", {
        customer_name: customer_name
    });
}