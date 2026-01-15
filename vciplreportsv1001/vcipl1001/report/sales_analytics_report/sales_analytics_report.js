frappe.query_reports["Sales Analytics Report"] = {
    filters: [
        {
            fieldname: "tree_type",
            label: __("Tree Type"),
            fieldtype: "Select",
            options: [
                "Customer Group",
                "Supplier",
                "Supplier Group",
                "Item",
                "Item Group",
                "Territory",
                "Project",
                "Order Type"
            ],
            default: "Customer Group",
            reqd: 1
        },
        {
            fieldname: "doc_type",
            label: __("Document Type"),
            fieldtype: "Select",
            options: [
                "Sales Invoice",
                "Sales Order",
                "Delivery Note"
            ],
            default: "Sales Invoice",
            reqd: 1
        },
        {
            fieldname: "value_quantity",
            label: __("Value / Quantity"),
            fieldtype: "Select",
            options: ["Value", "Quantity"],
            default: "Value",
            reqd: 1
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        },
        {
            fieldname: "range",
            label: __("Range"),
            fieldtype: "Select",
            options: ["Monthly", "Quarterly", "Yearly"],
            default: "Monthly",
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },

        // 🔽 CUSTOMER MASTER–BASED FILTERS
        {
            fieldname: "customer_group",
            label: __("Customer Group"),
            fieldtype: "Link",
            options: "Customer Group"
        },
        {
            fieldname: "custom_sub_group",
            label: __("Sub Group"),
            fieldtype: "Data"
        },
        {
            fieldname: "custom_company_type",
            label: __("Company Type"),
            fieldtype: "Select",
            options: "\nProprietor\nPartnership\nPrivate Limited\nGovernment"
        }
    ],

    /**
     * Formatter:
     * - indentation only
     * - no customer code handling needed (Python already fixed)
     */
    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data) return value;

        if (column.fieldname === "entity" && data.indent !== undefined) {
            value = `<span style="padding-left:${data.indent * 20}px">${value}</span>`;
        }

        return value;
    },

    /**
     * On load safety
     */
    onload: function (report) {
        // Enforce correct tree
        report.set_filter_value("tree_type", "Customer Group");
    }
};
