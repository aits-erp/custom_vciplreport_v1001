frappe.query_reports["Most Selling Below MSL Report"] = {
    onload: function (report) {
        report.set_filter_value("custom_item_type", "Finished Goods");

        // Default FY dates (April → March)
        let today = frappe.datetime.get_today();
        let d = frappe.datetime.str_to_obj(today);

        let year = d.getMonth() >= 3 ? d.getFullYear() : d.getFullYear() - 1;

        report.set_filter_value("from_date", `${year}-04-01`);
        report.set_filter_value("to_date", `${year + 1}-03-31`);
    },

    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data",
            default: "Finished Goods"
        },
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
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
