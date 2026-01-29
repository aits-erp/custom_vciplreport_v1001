frappe.query_reports["Stock Report - Cumulative"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_year_start()
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_year_end()
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "details" && data.item_code) {
            value = `
                <a href="#" class="view-warehouses"
                   data-item="${data.item_code}">
                   View Warehouses
                </a>`;
        }

        return value;
    }
};


// -----------------------------
// WAREHOUSE POPUP
// -----------------------------
$(document).on("click", ".view-warehouses", function (e) {
    e.preventDefault();

    const item_code = $(this).data("item");

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Bin",
            filters: { item_code },
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
                title: "Warehouse Stock for " + item_code,
                message: html,
                wide: true
            });
        }
    });
});
