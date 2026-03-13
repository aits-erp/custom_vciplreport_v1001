frappe.query_reports["FILL RATIO SALES ORDER"] = {

    filters: [

        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date"
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date"
        },

        {
            fieldname: "risk_filter",
            label: __("Risk Level"),
            fieldtype: "Select",
            options: ["", "HIGH", "Medium", "OK"]
        }

    ],

    formatter(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        // Clickable Available Qty
        if (column.fieldname === "available_qty") {

            value = `<a href="#" class="view-stock"
                        data-item="${data.item_code}">
                        ${data.available_qty || 0}
                    </a>`;
        }

        return value;
    }
};


// -------- WAREHOUSE POPUP --------

$(document).on("click", ".view-stock", function (e) {

    e.preventDefault();

    const item_code = $(this).data("item");

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Bin",
            filters: { item_code: item_code },
            fields: ["warehouse", "actual_qty"]
        },

        callback: function (r) {

            const rows = r.message || [];

            let html = `
                <table class="table table-bordered">
                    <tr>
                        <th>Warehouse</th>
                        <th>Stock Qty</th>
                    </tr>`;

            rows.forEach(row => {

                html += `
                    <tr>
                        <td>${row.warehouse}</td>
                        <td>${row.actual_qty}</td>
                    </tr>`;
            });

            html += "</table>";

            frappe.msgprint({
                title: "Warehouse Stock",
                message: html,
                wide: true
            });

        }
    });

});