frappe.query_reports["KBC Report"] = {

    filters: [
        {
            fieldname: "custom_item_type",
            label: __("Item Type"),
            fieldtype: "Data",
            default: "Finished Goods"
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

        // ── KBC Stock column → "View KBC" button ─────────────────────────
        if (column.fieldname === "kbc_stock") {
            return `<a href="#" class="kbc-popup"
                data-item="${data.item_code}"
                style="color:#2490ef;font-weight:500;white-space:nowrap">
                📦 View KBC
            </a>`;
        }

        return value;
    }
};


// ─────────────────────────────────────────────────────────────────────────────
// KBC POPUP — shows Kalvert / Buffing / Charak in 3 side-by-side columns
// Each column = warehouse-wise breakdown fetched from Bin
// ─────────────────────────────────────────────────────────────────────────────
$(document).on("click", ".kbc-popup", function(e) {
    e.preventDefault();

    const base_item = $(this).data("item");

    const k_item = base_item + "K";
    const b_item = base_item + "B";
    const c_item = base_item + "C";

    // Fetch all 3 KBC items in parallel
    Promise.all([
        get_bin_stock(k_item),
        get_bin_stock(b_item),
        get_bin_stock(c_item)
    ]).then(function([k_rows, b_rows, c_rows]) {

        // Collect all unique warehouses across all 3
        const all_warehouses = [];
        [k_rows, b_rows, c_rows].forEach(function(rows) {
            rows.forEach(function(r) {
                if (!all_warehouses.includes(r.warehouse)) {
                    all_warehouses.push(r.warehouse);
                }
            });
        });

        // Build warehouse → qty maps
        const k_map = build_map(k_rows);
        const b_map = build_map(b_rows);
        const c_map = build_map(c_rows);

        // Totals
        const k_total = k_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
        const b_total = b_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
        const c_total = c_rows.reduce((s, r) => s + flt(r.actual_qty), 0);

        // Build table rows
        let body_rows = "";

        if (all_warehouses.length === 0) {
            body_rows = `
                <tr>
                    <td colspan="4"
                        style="text-align:center;padding:12px;color:#888">
                        No KBC stock found for ${base_item}
                    </td>
                </tr>`;
        } else {
            all_warehouses.forEach(function(wh) {
                const k_qty = flt(k_map[wh] || 0);
                const b_qty = flt(b_map[wh] || 0);
                const c_qty = flt(c_map[wh] || 0);

                // Only show row if at least one has qty
                if (k_qty === 0 && b_qty === 0 && c_qty === 0) return;

                body_rows += `
                    <tr>
                        <td style="padding:6px 10px">${wh}</td>
                        <td style="padding:6px 10px;text-align:right;font-weight:500">
                            ${k_qty > 0 ? k_qty : '<span style="color:#ccc">—</span>'}
                        </td>
                        <td style="padding:6px 10px;text-align:right;font-weight:500">
                            ${b_qty > 0 ? b_qty : '<span style="color:#ccc">—</span>'}
                        </td>
                        <td style="padding:6px 10px;text-align:right;font-weight:500">
                            ${c_qty > 0 ? c_qty : '<span style="color:#ccc">—</span>'}
                        </td>
                    </tr>`;
            });
        }

        // Total row
        const total_row = `
            <tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
                <td style="padding:6px 10px">Total</td>
                <td style="padding:6px 10px;text-align:right">${flt(k_total, 2)}</td>
                <td style="padding:6px 10px;text-align:right">${flt(b_total, 2)}</td>
                <td style="padding:6px 10px;text-align:right">${flt(c_total, 2)}</td>
            </tr>`;

        frappe.msgprint({
            title: __("KBC Stock : " + base_item),
            message: `
                <table class="table table-bordered"
                       style="margin:0;width:100%;min-width:500px">
                    <thead style="background:#e8f0fe">
                        <tr>
                            <th style="padding:8px 10px;min-width:200px">
                                Warehouse
                            </th>
                            <th style="padding:8px 10px;text-align:right;color:#1a73e8">
                                Kalvert<br>
                                <small style="font-weight:normal">${k_item}</small>
                            </th>
                            <th style="padding:8px 10px;text-align:right;color:#e67e22">
                                Buffing<br>
                                <small style="font-weight:normal">${b_item}</small>
                            </th>
                            <th style="padding:8px 10px;text-align:right;color:#27ae60">
                                Charak<br>
                                <small style="font-weight:normal">${c_item}</small>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        ${body_rows}
                        ${total_row}
                    </tbody>
                </table>`,
            wide: true
        });
    });
});


// ── Helpers ──────────────────────────────────────────────────────────────────

function get_bin_stock(item_code) {
    return new Promise(function(resolve) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Bin",
                filters: { item_code: item_code },
                fields:  ["warehouse", "actual_qty"],
                limit_page_length: 50
            },
            callback: function(r) {
                resolve(r.message || []);
            }
        });
    });
}

function build_map(rows) {
    const map = {};
    rows.forEach(function(r) {
        map[r.warehouse] = flt(r.actual_qty);
    });
    return map;
}