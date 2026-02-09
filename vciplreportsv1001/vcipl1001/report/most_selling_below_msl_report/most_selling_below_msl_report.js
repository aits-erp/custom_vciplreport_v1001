frappe.query_reports["Most Selling Below MSL Report"] = {
    onload: function (report) {
        report.set_filter_value("custom_item_type", "Finished Goods");
    },

    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data",
            default: "Finished Goods"
        },
        {
            fieldname: "item_code",
            label: __("Item Code"),
            fieldtype: "Link",
            options: "Item"
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


// -------- WAREHOUSE POPUP --------
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
                title: "Warehouse Stock",
                message: html,
                wide: true
            });
        }
    });
});
