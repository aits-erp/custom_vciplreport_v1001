frappe.query_reports["Test1011"] = {

    // ─────────────────────────────────────────────────────────────────────
    // onload: pre-populate Category dropdown options WITHOUT forcing them
    // as the selected filter value. Your original code called
    // set_filter_value() which auto-selected all categories on every load —
    // that caused the report to always run with every category pre-ticked,
    // making the filter useless. Now we just leave it empty so the user
    // can pick what they need (or leave blank = all categories).
    // ─────────────────────────────────────────────────────────────────────
    onload: function(report) {
        // intentionally empty — Category filter populates dynamically via get_data
    },

    filters: [

        // ── Date range ────────────────────────────────────────────────────
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 1
        },

        // ── TSO ───────────────────────────────────────────────────────────
        {
            fieldname: "sales_person",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person",
            get_query: function() {
                return { filters: { is_group: 0 } };
            }
        },

        // ── Head Sales Person ─────────────────────────────────────────────
        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ── Region ────────────────────────────────────────────────────────
        {
            fieldname: "custom_region",
            label: "Region",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Sales Person", {
                    fields: ["custom_region"],
                    filters: [
                        ["custom_region", "!=", ""],
                        ["custom_region", "like", "%" + txt + "%"]
                    ],
                    group_by: "custom_region",
                    limit: 50
                }).then(function(rows) {
                    return [...new Set(rows.map(r => r.custom_region).filter(Boolean))]
                        .sort()
                        .map(v => ({ label: v, value: v }));
                });
            }
        },

        // ── Head Sales Code ───────────────────────────────────────────────
        {
            fieldname: "custom_head_sales_code",
            label: "Head Sales Code",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Sales Person", {
                    fields: ["custom_head_sales_code"],
                    filters: [
                        ["custom_head_sales_code", "!=", ""],
                        ["custom_head_sales_code", "like", "%" + txt + "%"]
                    ],
                    group_by: "custom_head_sales_code",
                    limit: 50
                }).then(function(rows) {
                    return [...new Set(rows.map(r => r.custom_head_sales_code).filter(Boolean))]
                        .sort()
                        .map(v => ({ label: v, value: v }));
                });
            }
        },

        // ── Customer ──────────────────────────────────────────────────────
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },

        // ── Customer Group ────────────────────────────────────────────────
        {
            fieldname: "customer_group",
            label: "Customer Group",
            fieldtype: "Link",
            options: "Customer Group",
            default: "Debtors Distributors"
        },

        // ── Category ──────────────────────────────────────────────────────
        {
            fieldname: "custom_main_group",
            label: "Category",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Item", {
                    fields: ["custom_main_group"],
                    filters: [
                        ["custom_main_group", "!=", ""],
                        ["custom_main_group", "like", "%" + txt + "%"]
                    ],
                    group_by: "custom_main_group",
                    limit: 100
                }).then(function(rows) {
                    return [...new Set(rows.map(r => r.custom_main_group).filter(Boolean))]
                        .sort()
                        .map(v => ({ label: v, value: v }));
                });
            }
        },

        // ── Item detail toggle ────────────────────────────────────────────
        {
            fieldname: "show_item_details",
            label: "Include Item Code & Item Name",
            fieldtype: "Check",
            default: 0
        }
    ],

    // ─────────────────────────────────────────────────────────────────────
    // formatter: colour-code Ach %, achieved vs target columns
    // ─────────────────────────────────────────────────────────────────────
    formatter: function(value, row, column, data, default_formatter) {
        let formatted = default_formatter(value, row, column, data);
        if (!data) return formatted;

        // Ach % column
        if (column.fieldname === "ach_pct") {
            if (value >= 100) {
                return `<span style="color:#00a36c; font-weight:bold;">${value}%</span>`;
            } else if (value >= 75) {
                return `<span style="color:#f0a500; font-weight:bold;">${value}%</span>`;
            } else if (value > 0) {
                return `<span style="color:#e03c31; font-weight:bold;">${value}%</span>`;
            } else {
                return `<span style="color:#aaa;">0%</span>`;
            }
        }

        // Any category *_achieved column: green if >= its target, red if below
        if (column.fieldname && column.fieldname.endsWith("_achieved")) {
            const targetField = column.fieldname.replace("_achieved", "_target");
            const target = data[targetField];
            if (target > 0) {
                if (value >= target) {
                    return `<span style="color:#00a36c; font-weight:bold;">${formatted}</span>`;
                } else if (value > 0) {
                    return `<span style="color:#e03c31;">${formatted}</span>`;
                }
            }
        }

        // Total Achieved vs Total Target
        if (column.fieldname === "total_achieved" && data.total_target > 0) {
            if (value >= data.total_target) {
                return `<span style="color:#00a36c; font-weight:bold;">${formatted}</span>`;
            } else if (value > 0) {
                return `<span style="color:#e03c31;">${formatted}</span>`;
            }
        }

        return formatted;
    },

    // ─────────────────────────────────────────────────────────────────────
    // Freeze first 3 columns (Month, TSO, Customer) while scrolling right
    // across all the category columns
    // ─────────────────────────────────────────────────────────────────────
    get_datatable_options: function(options) {
        return Object.assign(options, {
            freezeColumnsAt: 3
        });
    }
};