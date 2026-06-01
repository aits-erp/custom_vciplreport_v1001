frappe.query_reports["KBC Report"] = {

    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Select",
            // Blank default = show ALL items
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

    formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        // ── Item Code → clickable link ────────────────────────────────────
        if (column.fieldname === "item_code") {
            return `<a href="/app/item/${data.item_code}" target="_blank">${data.item_code}</a>`;
        }

        // ── Kalvert Qty ───────────────────────────────────────────────────
        if (column.fieldname === "kalvert_qty") {
            if (flt(data.kalvert_qty) > 0) {
                return `<a href="#" class="kbc-popup"
                    data-item="${data.item_code}K"
                    data-label="Kalvert"
                    style="color:#2490ef;font-weight:500">
                    ${flt(data.kalvert_qty, 2)}
                </a>`;
            }
            return `<span style="color:#aaa">0</span>`;
        }

        // ── Buffing Qty ───────────────────────────────────────────────────
        if (column.fieldname === "buffing_qty") {
            if (flt(data.buffing_qty) > 0) {
                return `<a href="#" class="kbc-popup"
                    data-item="${data.item_code}B"
                    data-label="Buffing"
                    style="color:#2490ef;font-weight:500">
                    ${flt(data.buffing_qty, 2)}
                </a>`;
            }
            return `<span style="color:#aaa">0</span>`;
        }

        // ── Charak Qty ────────────────────────────────────────────────────
        if (column.fieldname === "charak_qty") {
            if (flt(data.charak_qty) > 0) {
                return `<a href="#" class="kbc-popup"
                    data-item="${data.item_code}C"
                    data-label="Charak"
                    style="color:#2490ef;font-weight:500">
                    ${flt(data.charak_qty, 2)}
                </a>`;
            }
            return `<span style="color:#aaa">0</span>`;
        }

        return value;
    }
};


// ─────────────────────────────────────────────────────────────────────────────
// POPUP  –  Warehouse-wise stock using frappe.client.get_list (no custom method)
// ─────────────────────────────────────────────────────────────────────────────
$(document).on("click", ".kbc-popup", function(e) {
    e.preventDefault();

    const item_code = $(this).data("item");
    const label     = $(this).data("label");

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Bin",
            filters: { item_code: item_code },
            fields:  ["warehouse", "actual_qty"],
            limit_page_length: 50
        },
        callback: function(r) {
            const rows = r.message || [];

            let total     = 0;
            let tableRows = "";

            if (rows.length) {
                rows.forEach(function(d) {
                    total += flt(d.actual_qty);
                    tableRows += `
                        <tr>
                            <td style="padding:6px 10px">${d.warehouse}</td>
                            <td style="padding:6px 10px;text-align:right;font-weight:500">
                                ${flt(d.actual_qty, 2)}
                            </td>
                        </tr>`;
                });

                tableRows += `
                    <tr style="border-top:2px solid #ccc;font-weight:bold">
                        <td style="padding:6px 10px">Total</td>
                        <td style="padding:6px 10px;text-align:right">${flt(total, 2)}</td>
                    </tr>`;
            } else {
                tableRows = `
                    <tr>
                        <td colspan="2"
                            style="text-align:center;padding:12px;color:#888">
                            No stock found
                        </td>
                    </tr>`;
            }

            frappe.msgprint({
                title: __(`${label} Stock : ${item_code}`),
                message: `
                    <table class="table table-bordered"
                           style="margin:0;width:100%">
                        <thead style="background:#f0f4f8">
                            <tr>
                                <th style="padding:8px 10px">Warehouse</th>
                                <th style="padding:8px 10px;text-align:right">Qty</th>
                            </tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>`,
                wide: true
            });
        }
    });
});