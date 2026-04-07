frappe.query_reports["TSO WISE CATEGORYWISE"] = {

    onload: function(report) {
        // MultiSelectList needs a small delay after DOM is ready
        setTimeout(function() {
            report.set_filter_value("custom_main_group", [
                "Hard Anodised",
                "Nonstick",
                "Horeca",
                "Pressure Cookers",
                "SS Cookware",
                "Healux",
                "Kraft",
                "Platinum",
                "Platinum Triply P.cooker",
                "Cast Iron",
                "Kraft Pressure Cooker",
                "Csd",
                "Cookers Spare Parts",
                "Other Spare"
            ]);
        }, 500);
    },

    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 1
        },
        {
            fieldname: "sales_person",
            label: __("TSO"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "parent_sales_person",
            label: __("Head Sales Person"),
            fieldtype: "Link",
            options: "Sales Person"
        },
        {
            fieldname: "custom_region",
            label: __("Region"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Sales Person", {
                    fields: ["distinct custom_region as label"],
                    filters: [
                        ["custom_region", "!=", ""],
                        ["custom_region", "like", "%" + (txt || "") + "%"]
                    ],
                    limit: 50
                }).then(rows => rows.map(r => ({ value: r.label, description: "" })));
            }
        },
        {
            fieldname: "custom_head_sales_code",
            label: __("Head Sales Code"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Sales Person", {
                    fields: ["distinct custom_head_sales_code as label"],
                    filters: [
                        ["custom_head_sales_code", "!=", ""],
                        ["custom_head_sales_code", "like", "%" + (txt || "") + "%"]
                    ],
                    limit: 50
                }).then(rows => rows.map(r => ({ value: r.label, description: "" })));
            }
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "customer_group",
            label: __("Customer Group"),
            fieldtype: "Link",
            options: "Customer Group"
        },
        {
            fieldname: "custom_main_group",
            label: __("Category"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_list("Item", {
                    fields: ["distinct custom_main_group as label"],
                    filters: [
                        ["custom_main_group", "!=", ""],
                        ["custom_main_group", "like", "%" + (txt || "") + "%"]
                    ],
                    limit: 100
                }).then(rows => rows.map(r => ({ value: r.label, description: "" })));
            }
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data || value === null || value === undefined) return value;

        const fieldname = column.fieldname || "";
        const raw = data[column.fieldname];

        // ── Percent columns ──
        if (fieldname === "pct_achieved" || fieldname.endsWith("_pct")) {
            const pct = flt(raw);
            if (pct >= 100) {
                value = `<span style="color:var(--green-500,#28a745);font-weight:600">${value}</span>`;
            } else if (pct >= 75) {
                value = `<span style="color:var(--orange-500,#fd7e14);font-weight:600">${value}</span>`;
            } else if (pct > 0) {
                value = `<span style="color:var(--red-500,#dc3545);font-weight:500">${value}</span>`;
            }
            return value;
        }

        // ── Achieved columns ──
        if (fieldname === "total_achieved" || fieldname.endsWith("_achieved")) {
            const num = flt(raw);
            if (num > 0) {
                value = `<span style="color:var(--green-600,#218838);font-weight:600">${value}</span>`;
            } else {
                value = `<span style="color:var(--red-400,#e06666)">${value}</span>`;
            }
            return value;
        }

        // ── Target columns ──
        if (fieldname === "total_target" || fieldname.endsWith("_target")) {
            const num = flt(raw);
            if (num > 0) {
                value = `<span style="color:var(--blue-600,#0056b3);font-weight:600">${value}</span>`;
            }
            return value;
        }

        return value;
    },

    // ── Highlight row red if overall % < 50, orange if < 100 ──
    get_datatable_options: function(options) {
        options.getRowHTML = function(cells, props) {
            return null; // let default handle it
        };
        return options;
    }
};

// Utility to safely parse float (avoids NaN on non-numeric strings)
function flt(val) {
    const n = parseFloat(val);
    return isNaN(n) ? 0 : n;
}