// ─────────────────────────────────────────────────────────────
//  KBC Report – kbc_report.js
//  No custom method path – uses frappe.client.get_list only
// ─────────────────────────────────────────────────────────────

frappe.query_reports["KBC Report"] = {

    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Select",
            options: "\nFinished Goods\nSemi Finished Goods\nRaw Material",
            default: ""
        },
        {
            fieldname: "custom_main_group",
            label: __("Main Group"),
            fieldtype: "Data"
        },
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
        }
    ],

    // ── formatter ─────────────────────────────────────────────────────
    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        // Item Code → clickable link to item master
        if (column.fieldname === "item_code") {
            return `<a href="/app/item/${data.item_code}" target="_blank">${data.item_code}</a>`;
        }

        // Kalvert → clickable if qty > 0, opens warehouse popup for item_code + "K"
        if (column.fieldname === "kalvert_qty" && flt(data.kalvert_qty) > 0) {
            return `<a href="#" class="kbc-wh-popup"
                        data-item="${data.item_code}K"
                        data-label="Kalvert">
                        ${flt(data.kalvert_qty, 3)}
                    </a>`;
        }

        // Buffing → clickable if qty > 0, opens warehouse popup for item_code + "B"
        if (column.fieldname === "buffing_qty" && flt(data.buffing_qty) > 0) {
            return `<a href="#" class="kbc-wh-popup"
                        data-item="${data.item_code}B"
                        data-label="Buffing">
                        ${flt(data.buffing_qty, 3)}
                    </a>`;
        }

        // Charak → clickable if qty > 0, opens warehouse popup for item_code + "C"
        if (column.fieldname === "charak_qty" && flt(data.charak_qty) > 0) {
            return `<a href="#" class="kbc-wh-popup"
                        data-item="${data.item_code}C"
                        data-label="Charak">
                        ${flt(data.charak_qty, 3)}
                    </a>`;
        }

        return value;
    }
};


// ── warehouse popup (no custom method – uses frappe.client.get_list) ──
$(document).on("click", ".kbc-wh-popup", function (e) {
    e.preventDefault();

    const item_code = $(this).data("item");
    const label     = $(this).data("label");

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Bin",
            filters:  { item_code: item_code },
            fields:   ["warehouse", "actual_qty"],
            limit_page_length: 100
        },
        callback: function (r) {
            const rows = (r.message || []).filter(d => d.actual_qty > 0);

            let html = `
                <table class="table table-bordered" style="margin:0;">
                    <thead>
                        <tr>
                            <th>Warehouse</th>
                            <th style="text-align:right;">Qty</th>
                        </tr>
                    </thead>
                    <tbody>`;

            if (rows.length) {
                rows.forEach(function (d) {
                    html += `
                        <tr>
                            <td>${d.warehouse}</td>
                            <td style="text-align:right;">${flt(d.actual_qty, 3)}</td>
                        </tr>`;
                });
            } else {
                html += `<tr><td colspan="2" style="text-align:center;">No stock found</td></tr>`;
            }

            html += `</tbody></table>`;

            frappe.msgprint({
                title: __(`${label} – Warehouse Stock : ${item_code}`),
                message: html,
                wide: true
            });
        }
    });
});