frappe.query_reports["CATEGORYWISE"] = {

    filters: [

        // ✅ Date
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end()
        },

        // ✅ TSO
        {
            fieldname: "tso",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person",
            get_query: function () {
                return { filters: { is_group: 0 } };
            }
        },

        // ✅ Parent Sales Person (🔥 NEW)
        {
            fieldname: "parent_sales_person",
            label: "Parent Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ✅ Customer
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },

        // ✅ Category
        {
            fieldname: "item_group",
            label: "Category",
            fieldtype: "Link",
            options: "Item Group"
        },

        // ✅ Main Group
        {
            fieldname: "main_group",
            label: "Main Group",
            fieldtype: "Data"
        },

        // ✅ Item
        {
            fieldname: "item",
            label: "Item",
            fieldtype: "Link",
            options: "Item"
        },

        // ✅ Warehouse
        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Warehouse"
        },

        // ✅ Company
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        },

        // 🔥 Toggle Category
        {
            fieldname: "show_category",
            label: "Show Category",
            fieldtype: "Check",
            default: 0
        },

        // 🔥 Toggle Item
        {
            fieldname: "show_item",
            label: "Show Item",
            fieldtype: "Check",
            default: 0
        }

    ],

    // 🔥 Drill Down
    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "amount" && data && data.customer) {
            return `<a href="#" onclick="open_invoice('${data.customer}')">${value}</a>`;
        }

        return value;
    }
};

function open_invoice(customer) {
    frappe.set_route("List", "Sales Invoice", {
        customer: customer
    });
}