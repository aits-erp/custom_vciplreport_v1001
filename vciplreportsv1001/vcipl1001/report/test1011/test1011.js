frappe.query_reports["TSO WISE CATEGORYWISE"] = {

    // ─────────────────────────────────────────────────────────────────────
    // onload: populate the Category multiselect with all available groups.
    // FIX: Do NOT set it as a default — only pre-populate the dropdown list
    //      so the user can pick from them. Forcing all categories as the
    //      default filter value caused the report to always open pre-filtered
    //      and confused users who wanted "all categories".
    // ─────────────────────────────────────────────────────────────────────
    onload: function(report) {
        // Nothing forced here — get_data in the filter handles dynamic loading.
        // We keep this hook in case you want to set defaults later.
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

        // ── TSO (single Sales Person) ─────────────────────────────────────
        {
            fieldname: "sales_person",
            label: "TSO",
            fieldtype: "Link",
            options: "Sales Person",
            // Only show leaf-level sales persons (TSOs), not managers
            get_query: function() {
                return {
                    filters: { "is_group": 0 }
                };
            }
        },

        // ── Head Sales Person (manager above TSO) ─────────────────────────
        {
            fieldname: "parent_sales_person",
            label: "Head Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        },

        // ── Region (multi-select, dynamic) ────────────────────────────────
        {
            fieldname: "custom_region",
            label: "Region",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Sales Person", {
                    fields: ["custom_region"],
                    filters: [
                        ["custom_region", "!=", ""],
                        ["custom_region", "like", `%${txt}%`]
                    ],
                    group_by: "custom_region",
                    limit: 50
                }).then(rows => {
                    const unique = [...new Set(
                        rows.map(r => r.custom_region).filter(Boolean)
                    )].sort();
                    return unique.map(v => ({ label: v, value: v }));
                });
            }
        },

        // ── Head Sales Code (multi-select, dynamic) ───────────────────────
        {
            fieldname: "custom_head_sales_code",
            label: "Head Sales Code",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Sales Person", {
                    fields: ["custom_head_sales_code"],
                    filters: [
                        ["custom_head_sales_code", "!=", ""],
                        ["custom_head_sales_code", "like", `%${txt}%`]
                    ],
                    group_by: "custom_head_sales_code",
                    limit: 50
                }).then(rows => {
                    const unique = [...new Set(
                        rows.map(r => r.custom_head_sales_code).filter(Boolean)
                    )].sort();
                    return unique.map(v => ({ label: v, value: v }));
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

        // ── Category / Main Group (multi-select, dynamic) ─────────────────
        {
            fieldname: "custom_main_group",
            label: "Category",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Item", {
                    fields: ["custom_main_group"],
                    filters: [
                        ["custom_main_group", "!=", ""],
                        ["custom_main_group", "like", `%${txt}%`]
                    ],
                    group_by: "custom_main_group",
                    limit: 100
                }).then(rows => {
                    const unique = [...new Set(
                        rows.map(r => r.custom_main_group).filter(Boolean)
                    )].sort();
                    return unique.map(v => ({ label: v, value: v }));
                });
            }
        },

        // ── Toggle: include item-level detail columns ─────────────────────
        {
            fieldname: "show_item_details",
            label: "Include Item Code & Item Name",
            fieldtype: "Check",
            default: 0
        }
    ],

    // ─────────────────────────────────────────────────────────────────────
    // formatter: colour-code the Ach % column and achieved cells
    // ─────────────────────────────────────────────────────────────────────
    formatter: function(value, row, column, data, default_formatter) {
        let formatted = default_formatter(value, row, column, data);

        if (!data) return formatted;

        // Ach % column — colour by threshold
        if (column.fieldname === "ach_pct") {
            if (value >= 100) {
                formatted = `<span style="color:#00a36c;font-weight:bold;">${value}%</span>`;
            } else if (value >= 75) {
                formatted = `<span style="color:#f0a500;font-weight:bold;">${value}%</span>`;
            } else if (value > 0) {
                formatted = `<span style="color:#e03c31;font-weight:bold;">${value}%</span>`;
            } else {
                formatted = `<span style="color:#aaa;">0%</span>`;
            }
        }

        // Any *_achieved column — compare against matching *_target column
        if (column.fieldname && column.fieldname.endsWith("_achieved")) {
            const targetField = column.fieldname.replace("_achieved", "_target");
            const target = data[targetField];
            if (target > 0) {
                if (value >= target) {
                    formatted = `<span style="color:#00a36c;font-weight:bold;">${formatted}</span>`;
                } else if (value > 0) {
                    formatted = `<span style="color:#e03c31;">${formatted}</span>`;
                }
            }
        }

        // Total Achieved vs Total Target
        if (column.fieldname === "total_achieved" && data.total_target > 0) {
            if (value >= data.total_target) {
                formatted = `<span style="color:#00a36c;font-weight:bold;">${formatted}</span>`;
            } else if (value > 0) {
                formatted = `<span style="color:#e03c31;">${formatted}</span>`;
            }
        }

        return formatted;
    },

    // ─────────────────────────────────────────────────────────────────────
    // get_datatable_options: freeze first few columns for horizontal scroll
    // ─────────────────────────────────────────────────────────────────────
    get_datatable_options: function(options) {
        return Object.assign(options, {
            // Freeze the Month + TSO + Customer columns while scrolling right
            freezeColumnsAt: 3
        });
    }
};