// Auto Financial Year calculation (Apr → Mar)
function get_default_fy_dates() {
    const today = frappe.datetime.get_today();
    const d = frappe.datetime.str_to_obj(today);

    let fy_start, fy_end;

    if ((d.getMonth() + 1) > 3) {
        fy_start = `${d.getFullYear()}-04-01`;
        fy_end = `${d.getFullYear() + 1}-03-31`;
    } else {
        fy_start = `${d.getFullYear() - 1}-04-01`;
        fy_end = `${d.getFullYear()}-03-31`;
    }

    return { fy_start, fy_end };
}

const fy = get_default_fy_dates();

frappe.query_reports["FILL RATIO SALES ORDER"] = {

    filters: [

        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: "Vinod Cookware India Private Limited",
            reqd: 1
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: fy.fy_start
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: fy.fy_end
        },

        {
            fieldname: "risk_filter",
            label: __("Risk Level"),
            fieldtype: "Select",
            options: ["", "HIGH", "Medium", "OK"],
            default: ""
        }

    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        if (column.fieldname === "risk") {

            if (data.risk === "Critical") {
                value = `<span style="color:red;font-weight:bold">🔴 HIGH</span>`;
            }

            if (data.risk === "Warning") {
                value = `<span style="color:orange;font-weight:bold">🟠 Medium</span>`;
            }

            if (data.risk === "OK") {
                value = `<span style="color:green;font-weight:bold">🟢 OK</span>`;
            }
        }

        if (column.fieldname === "fill_ratio") {

            if (data.fill_ratio < 50) {
                value = `<span style="color:red;font-weight:bold">${data.fill_ratio}%</span>`;
            } else if (data.fill_ratio < 80) {
                value = `<span style="color:orange;font-weight:bold">${data.fill_ratio}%</span>`;
            } else {
                value = `<span style="color:green;font-weight:bold">${data.fill_ratio}%</span>`;
            }
        }

        return value;
    }
};
