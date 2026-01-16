frappe.query_reports["Sales Analytics Report"] = {
    filters: [
        {
            fieldname: "mode",
            label: "Mode",
            fieldtype: "Select",
            options: ["Customer", "Item"],
            default: "Customer"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "metric",
            label: "Metric",
            fieldtype: "Select",
            options: ["Value", "Qty"],
            default: "Value"
        }
    ],

    onload(report) {
        report.breadcrumbs = [];
    },

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // 🔥 DRILL CLICK
        if (column.fieldname === "name" && data && data.drill) {
            return `
                <a style="font-weight:600;color:#1a73e8;cursor:pointer"
                   onclick='frappe.query_reports["Sales Analytics Report"]
                   .drill(${JSON.stringify(data.drill)})'>
                   ${value}
                </a>`;
        }

        return value;
    },

    // ====================================================
    // DRILL HANDLER
    // ====================================================
    drill(drill_data) {
        if (!drill_data) return;

        let d = JSON.parse(drill_data);

        let report = frappe.query_report;
        let filters = report.get_values();

        // save breadcrumb
        report.breadcrumbs.push({
            label: d.value || d.level,
            level: d.level
        });

        // apply next level
        filters.level = d.level;

        if (d.value) filters.value = d.value;
        if (d.customer) filters.customer = d.customer;
        if (d.item_code) filters.item_code = d.item_code;

        report.set_filter_value(filters);
        report.refresh();

        this.render_breadcrumbs();
    },

    // ====================================================
    // BREADCRUMBS UI
    // ====================================================
    render_breadcrumbs() {
        let report = frappe.query_report;

        if (!report.page) return;

        let html = report.breadcrumbs.map((b, i) => {
            return `<span style="cursor:pointer;color:#1a73e8"
                onclick='frappe.query_reports["Sales Analytics Report"].breadcrumb_click(${i})'>
                ${b.label}
            </span>`;
        }).join(" &gt; ");

        report.page.set_secondary_action(html);
    },

    breadcrumb_click(index) {
        let report = frappe.query_report;

        report.breadcrumbs = report.breadcrumbs.slice(0, index + 1);

        let crumb = report.breadcrumbs[index];
        let filters = report.get_values();

        filters.level = crumb.level;
        report.set_filter_value(filters);
        report.refresh();

        this.render_breadcrumbs();
    }
};
