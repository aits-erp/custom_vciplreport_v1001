// frappe.query_reports["Stock Report - Cumulative"] = {

//     filters: [
//         {
//             fieldname: "custom_item_type",
//             label: __("Item Type"),
//             fieldtype: "Data",
//             default: "Finished Goods"
//         },
//         {
//             fieldname: "custom_main_group",
//             label: __("Main Group"),
//             fieldtype: "Data"
//         },
//         {
//             fieldname: "item_group",
//             label: __("Item Group"),
//             fieldtype: "Link",
//             options: "Item Group"
//         },
//         {
//             fieldname: "from_date",
//             label: __("From Date"),
//             fieldtype: "Date",
//             default: "2025-04-01"
//         },
//         {
//             fieldname: "to_date",
//             label: __("To Date"),
//             fieldtype: "Date",
//             default: frappe.datetime.get_today()
//         }
//     ],

//     formatter: function(value, row, column, data, default_formatter) {

//         if (column.fieldname === "item_code") {
//             return `<a href="/app/item/${value}" target="_blank">${value}</a>`;
//         }

//         if (column.fieldname === "view_kbc" && data && data.item_code) {
//             return `<a href="#" class="kbc-open" data-item="${data.item_code}"
//                 style="color:#2490ef;font-weight:500">
//                 📦 View KBC
//             </a>`;
//         }

//         return default_formatter(value, row, column, data);
//     },

//     after_datatable_render: function(datatable) {
//         $(datatable.wrapper).off("click", ".kbc-open").on("click", ".kbc-open", function(e) {
//             e.preventDefault();
//             e.stopPropagation();
//             show_kbc_popup($(this).data("item"));
//         });
//     }
// };


// // ─────────────────────────────────────────────────────────────────────────────
// // STEP 1 — KBC popup
// // ─────────────────────────────────────────────────────────────────────────────
// function show_kbc_popup(base) {
//     Promise.all([
//         kbc_get_bin(base + "K"),
//         kbc_get_bin(base + "B"),
//         kbc_get_bin(base + "C")
//     ]).then(function([k_rows, b_rows, c_rows]) {

//         const k_total = k_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
//         const b_total = b_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
//         const c_total = c_rows.reduce((s, r) => s + flt(r.actual_qty), 0);

//         const warehouses = [];
//         [k_rows, b_rows, c_rows].forEach(rows => {
//             rows.forEach(r => {
//                 if (!warehouses.includes(r.warehouse)) warehouses.push(r.warehouse);
//             });
//         });

//         const k_map = kbc_build_map(k_rows);
//         const b_map = kbc_build_map(b_rows);
//         const c_map = kbc_build_map(c_rows);

//         let body = "";
//         if (warehouses.length === 0) {
//             body = `<tr><td colspan="4" style="text-align:center;padding:14px;color:#999">
//                 No KBC stock found for ${base}
//             </td></tr>`;
//         } else {
//             warehouses.forEach(wh => {
//                 const k = flt(k_map[wh] || 0);
//                 const b = flt(b_map[wh] || 0);
//                 const c = flt(c_map[wh] || 0);
//                 if (k === 0 && b === 0 && c === 0) return;
//                 body += `<tr>
//                     <td style="padding:6px 10px">${wh}</td>
//                     <td style="padding:6px 10px;text-align:right">
//                         ${k > 0
//                             ? `<a href="#" class="kbc-drill" data-item="${base}K" data-label="Kalvert"
//                                 style="color:#1a73e8;font-weight:500">${flt(k,2)}</a>`
//                             : `<span style="color:#ccc">—</span>`}
//                     </td>
//                     <td style="padding:6px 10px;text-align:right">
//                         ${b > 0
//                             ? `<a href="#" class="kbc-drill" data-item="${base}B" data-label="Buffing"
//                                 style="color:#e67e22;font-weight:500">${flt(b,2)}</a>`
//                             : `<span style="color:#ccc">—</span>`}
//                     </td>
//                     <td style="padding:6px 10px;text-align:right">
//                         ${c > 0
//                             ? `<a href="#" class="kbc-drill" data-item="${base}C" data-label="Charak"
//                                 style="color:#27ae60;font-weight:500">${flt(c,2)}</a>`
//                             : `<span style="color:#ccc">—</span>`}
//                     </td>
//                 </tr>`;
//             });
//         }

//         if (cur_dialog) cur_dialog.hide();

//         let d = new frappe.ui.Dialog({
//             title: __("KBC Stock : " + base),
//             fields: [{ fieldtype: "HTML", fieldname: "kbc_html" }]
//         });

//         d.fields_dict.kbc_html.$wrapper.html(`
//             <table class="table table-bordered" style="margin:0;width:100%;min-width:480px">
//                 <thead style="background:#e8f0fe">
//                     <tr>
//                         <th style="padding:8px 10px">Warehouse</th>
//                         <th style="padding:8px 10px;text-align:right;color:#1a73e8">
//                             Kalvert<br><small style="font-weight:normal">${base}K</small>
//                         </th>
//                         <th style="padding:8px 10px;text-align:right;color:#e67e22">
//                             Buffing<br><small style="font-weight:normal">${base}B</small>
//                         </th>
//                         <th style="padding:8px 10px;text-align:right;color:#27ae60">
//                             Charak<br><small style="font-weight:normal">${base}C</small>
//                         </th>
//                     </tr>
//                 </thead>
//                 <tbody>
//                     ${body}
//                     <tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
//                         <td style="padding:6px 10px">Total</td>
//                         <td style="padding:6px 10px;text-align:right">${flt(k_total,2)}</td>
//                         <td style="padding:6px 10px;text-align:right">${flt(b_total,2)}</td>
//                         <td style="padding:6px 10px;text-align:right">${flt(c_total,2)}</td>
//                     </tr>
//                 </tbody>
//             </table>
//             <p style="margin:8px 0 0;font-size:11px;color:#999">
//                 💡 Click any quantity to see warehouse-wise breakdown
//             </p>
//         `);

//         d.fields_dict.kbc_html.$wrapper.on("click", ".kbc-drill", function(e) {
//             e.preventDefault();
//             d.hide();
//             show_kbc_drill($(this).data("item"), $(this).data("label"), base);
//         });

//         d.set_primary_btn(__("Close"), () => d.hide());
//         d.show();
//     });
// }


// // ─────────────────────────────────────────────────────────────────────────────
// // STEP 2 — Warehouse drill-down
// // ─────────────────────────────────────────────────────────────────────────────
// function show_kbc_drill(item_code, label, base) {
//     frappe.call({
//         method: "frappe.client.get_list",
//         args: {
//             doctype: "Bin",
//             filters: { item_code: item_code },
//             fields: ["warehouse", "actual_qty"],
//             limit_page_length: 50
//         },
//         callback: function(r) {
//             const rows  = r.message || [];
//             const total = rows.reduce((s, d) => s + flt(d.actual_qty), 0);

//             let body = "";
//             if (rows.length) {
//                 rows.forEach(d => {
//                     body += `<tr>
//                         <td style="padding:6px 10px">${d.warehouse}</td>
//                         <td style="padding:6px 10px;text-align:right;font-weight:500">
//                             ${flt(d.actual_qty, 2)}
//                         </td>
//                     </tr>`;
//                 });
//                 body += `<tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
//                     <td style="padding:6px 10px">Total</td>
//                     <td style="padding:6px 10px;text-align:right">${flt(total,2)}</td>
//                 </tr>`;
//             } else {
//                 body = `<tr><td colspan="2" style="text-align:center;padding:12px;color:#999">
//                     No stock found
//                 </td></tr>`;
//             }

//             let d2 = new frappe.ui.Dialog({
//                 title: __(`${label} Warehouse Stock : ${item_code}`),
//                 fields: [{ fieldtype: "HTML", fieldname: "wh_html" }]
//             });

//             d2.fields_dict.wh_html.$wrapper.html(`
//                 <table class="table table-bordered" style="margin:0;width:100%">
//                     <thead style="background:#f0f4f8">
//                         <tr>
//                             <th style="padding:8px 10px">Warehouse</th>
//                             <th style="padding:8px 10px;text-align:right">Qty</th>
//                         </tr>
//                     </thead>
//                     <tbody>${body}</tbody>
//                 </table>
//             `);

//             d2.add_custom_btn(__("← Back to KBC"), () => { d2.hide(); show_kbc_popup(base); });
//             d2.set_primary_btn(__("Close"), () => d2.hide());
//             d2.show();
//         }
//     });
// }


// // ── Helpers ──────────────────────────────────────────────────────────────────
// function kbc_get_bin(item_code) {
//     return new Promise(function(resolve) {
//         frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Bin",
//                 filters: { item_code: item_code },
//                 fields: ["warehouse", "actual_qty"],
//                 limit_page_length: 50
//             },
//             callback: function(r) { resolve(r.message || []); }
//         });
//     });
// }

// function kbc_build_map(rows) {
//     const map = {};
//     rows.forEach(r => { map[r.warehouse] = flt(r.actual_qty); });
//     return map;
// }

// frappe.query_reports["Stock Report - Cumulative"] = {

//     filters: [
//         {
//             fieldname: "custom_item_type",
//             label: __("Item Type"),
//             fieldtype: "Data",
//             default: "Finished Goods"
//         },
//         {
//             fieldname: "custom_main_group",
//             label: __("Main Group"),
//             fieldtype: "Data"
//         },
//         {
//             fieldname: "item_group",
//             label: __("Item Group"),
//             fieldtype: "Link",
//             options: "Item Group"
//         },
//         {
//             fieldname: "from_date",
//             label: __("From Date"),
//             fieldtype: "Date",
//             default: "2025-04-01"
//         },
//         {
//             fieldname: "to_date",
//             label: __("To Date"),
//             fieldtype: "Date",
//             default: frappe.datetime.get_today()
//         }
//     ],

//     formatter: function(value, row, column, data, default_formatter) {

//         // ── Item Code → click opens KBC popup ──
//         if (column.fieldname === "item_code" && data && data.item_code) {
//             return `<a href="#" class="kbc-open" data-item="${data.item_code}"
//                 style="color:#2490ef;font-weight:600;text-decoration:none">
//                 ${value}
//             </a>`;
//         }

//         return default_formatter(value, row, column, data);
//     },

//     after_datatable_render: function(datatable) {
//         $(datatable.wrapper).off("click", ".kbc-open").on("click", ".kbc-open", function(e) {
//             e.preventDefault();
//             e.stopPropagation();
//             show_kbc_popup($(this).data("item"));
//         });
//     }
// };


// // ─────────────────────────────────────────────────────────────────────────────
// // STEP 1 — KBC popup (opens on Item Code click)
// // ─────────────────────────────────────────────────────────────────────────────
// function show_kbc_popup(base) {

//     frappe.dom.freeze(__("Loading KBC stock..."));

//     Promise.all([
//         kbc_get_bin(base + "K"),
//         kbc_get_bin(base + "B"),
//         kbc_get_bin(base + "C")
//     ]).then(function(results) {

//         frappe.dom.unfreeze();

//         const k_rows = results[0];
//         const b_rows = results[1];
//         const c_rows = results[2];

//         const k_total = k_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
//         const b_total = b_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
//         const c_total = c_rows.reduce((s, r) => s + flt(r.actual_qty), 0);

//         // unique warehouse list across K / B / C
//         const warehouses = [];
//         [k_rows, b_rows, c_rows].forEach(rows => {
//             rows.forEach(r => {
//                 if (!warehouses.includes(r.warehouse)) warehouses.push(r.warehouse);
//             });
//         });

//         const k_map = kbc_build_map(k_rows);
//         const b_map = kbc_build_map(b_rows);
//         const c_map = kbc_build_map(c_rows);

//         let body = "";
//         if (warehouses.length === 0) {
//             body = `<tr><td colspan="4" style="text-align:center;padding:14px;color:#999">
//                 No KBC stock found for ${base}
//             </td></tr>`;
//         } else {
//             warehouses.forEach(wh => {
//                 const k = flt(k_map[wh] || 0);
//                 const b = flt(b_map[wh] || 0);
//                 const c = flt(c_map[wh] || 0);
//                 if (k === 0 && b === 0 && c === 0) return;
//                 body += `<tr>
//                     <td style="padding:6px 10px">${wh}</td>
//                     <td style="padding:6px 10px;text-align:right">
//                         ${k > 0
//                             ? `<a href="#" class="kbc-drill" data-item="${base}K" data-label="Kalvert"
//                                 style="color:#1a73e8;font-weight:500">${flt(k,2)}</a>`
//                             : `<span style="color:#ccc">—</span>`}
//                     </td>
//                     <td style="padding:6px 10px;text-align:right">
//                         ${b > 0
//                             ? `<a href="#" class="kbc-drill" data-item="${base}B" data-label="Buffing"
//                                 style="color:#e67e22;font-weight:500">${flt(b,2)}</a>`
//                             : `<span style="color:#ccc">—</span>`}
//                     </td>
//                     <td style="padding:6px 10px;text-align:right">
//                         ${c > 0
//                             ? `<a href="#" class="kbc-drill" data-item="${base}C" data-label="Charak"
//                                 style="color:#27ae60;font-weight:500">${flt(c,2)}</a>`
//                             : `<span style="color:#ccc">—</span>`}
//                     </td>
//                 </tr>`;
//             });
//         }

//         let d = new frappe.ui.Dialog({
//             title: __("KBC Stock : " + base),
//             size: "large",
//             fields: [{ fieldtype: "HTML", fieldname: "kbc_html" }],
//             primary_action_label: __("Close"),
//             primary_action: function() { d.hide(); }
//         });

//         d.fields_dict.kbc_html.$wrapper.html(`
//             <table class="table table-bordered" style="margin:0;width:100%">
//                 <thead style="background:#e8f0fe">
//                     <tr>
//                         <th style="padding:8px 10px">Warehouse</th>
//                         <th style="padding:8px 10px;text-align:right;color:#1a73e8">
//                             Kalvert<br><small style="font-weight:normal">${base}K</small>
//                         </th>
//                         <th style="padding:8px 10px;text-align:right;color:#e67e22">
//                             Buffing<br><small style="font-weight:normal">${base}B</small>
//                         </th>
//                         <th style="padding:8px 10px;text-align:right;color:#27ae60">
//                             Charak<br><small style="font-weight:normal">${base}C</small>
//                         </th>
//                     </tr>
//                 </thead>
//                 <tbody>
//                     ${body}
//                     <tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
//                         <td style="padding:6px 10px">Total</td>
//                         <td style="padding:6px 10px;text-align:right">${flt(k_total,2)}</td>
//                         <td style="padding:6px 10px;text-align:right">${flt(b_total,2)}</td>
//                         <td style="padding:6px 10px;text-align:right">${flt(c_total,2)}</td>
//                     </tr>
//                 </tbody>
//             </table>
//             <p style="margin:8px 0 0;font-size:11px;color:#999">
//                 💡 Click any quantity to see warehouse-wise breakdown &nbsp;|&nbsp;
//                 <a href="/app/item/${base}" target="_blank" style="color:#2490ef">
//                     Open Item Master ↗
//                 </a>
//             </p>
//         `);

//         // qty click → drill-down
//         d.fields_dict.kbc_html.$wrapper.on("click", ".kbc-drill", function(e) {
//             e.preventDefault();
//             d.hide();
//             show_kbc_drill($(this).data("item"), $(this).data("label"), base);
//         });

//         d.show();

//     }).catch(function(err) {
//         frappe.dom.unfreeze();
//         console.error("KBC popup error:", err);
//         frappe.msgprint({
//             title: __("KBC Error"),
//             indicator: "red",
//             message: __("Error: ") + (err && err.message ? err.message : err)
//         });
//     });
// }


// // ─────────────────────────────────────────────────────────────────────────────
// // STEP 2 — Warehouse drill-down (click on any K / B / C qty)
// // ─────────────────────────────────────────────────────────────────────────────
// function show_kbc_drill(item_code, label, base) {
//     frappe.call({
//         method: "frappe.client.get_list",
//         args: {
//             doctype: "Bin",
//             filters: { item_code: item_code },
//             fields: ["warehouse", "actual_qty"],
//             limit_page_length: 50
//         },
//         callback: function(r) {
//             const rows  = r.message || [];
//             const total = rows.reduce((s, d) => s + flt(d.actual_qty), 0);

//             let body = "";
//             if (rows.length) {
//                 rows.forEach(d => {
//                     body += `<tr>
//                         <td style="padding:6px 10px">${d.warehouse}</td>
//                         <td style="padding:6px 10px;text-align:right;font-weight:500">
//                             ${flt(d.actual_qty, 2)}
//                         </td>
//                     </tr>`;
//                 });
//                 body += `<tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
//                     <td style="padding:6px 10px">Total</td>
//                     <td style="padding:6px 10px;text-align:right">${flt(total,2)}</td>
//                 </tr>`;
//             } else {
//                 body = `<tr><td colspan="2" style="text-align:center;padding:12px;color:#999">
//                     No stock found
//                 </td></tr>`;
//             }

//             let d2 = new frappe.ui.Dialog({
//                 title: __(`${label} Warehouse Stock : ${item_code}`),
//                 fields: [{ fieldtype: "HTML", fieldname: "wh_html" }],
//                 primary_action_label: __("Close"),
//                 primary_action: function() { d2.hide(); },
//                 secondary_action_label: __("← Back to KBC"),
//                 secondary_action: function() {
//                     d2.hide();
//                     show_kbc_popup(base);
//                 }
//             });

//             d2.fields_dict.wh_html.$wrapper.html(`
//                 <table class="table table-bordered" style="margin:0;width:100%">
//                     <thead style="background:#f0f4f8">
//                         <tr>
//                             <th style="padding:8px 10px">Warehouse</th>
//                             <th style="padding:8px 10px;text-align:right">Qty</th>
//                         </tr>
//                     </thead>
//                     <tbody>${body}</tbody>
//                 </table>
//             `);

//             d2.show();
//         }
//     });
// }


// // ── Helpers ──────────────────────────────────────────────────────────────────
// function kbc_get_bin(item_code) {
//     return new Promise(function(resolve) {
//         frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Bin",
//                 filters: { item_code: item_code },
//                 fields: ["warehouse", "actual_qty"],
//                 limit_page_length: 50
//             },
//             callback: function(r) { resolve(r.message || []); },
//             error: function() { resolve([]); }
//         });
//     });
// }

// function kbc_build_map(rows) {
//     const map = {};
//     rows.forEach(r => { map[r.warehouse] = flt(r.actual_qty); });
//     return map;
// }

frappe.query_reports["Stock Report - Cumulative"] = {

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
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: "2025-04-01"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {

        // ── Item Code → click opens KBC popup ──
        if (column.fieldname === "item_code" && data && data.item_code) {
            return `<a href="#" class="kbc-open" data-item="${data.item_code}"
                style="color:#2490ef;font-weight:600;text-decoration:none">
                ${value}
            </a>`;
        }

        return default_formatter(value, row, column, data);
    },

    // after_datatable_render: function(datatable) {
    after_datatable_render: function(datatable) {

        if (!$("#kbc-row-highlight-style").length) {
            $("<style>")
                .attr("id", "kbc-row-highlight-style")
                .html(`
                    .dt-cell.kbc-row-highlight {
                        background-color: #d6e9ff !important;
                    }
                `)
                .appendTo("head");
        }

        function highlight_row($cell) {
            const rowIndex = $cell.attr("data-row-index");
            if (rowIndex === undefined) return;
            $(datatable.wrapper).find(".dt-cell").removeClass("kbc-row-highlight");
            $(datatable.wrapper).find(`.dt-cell[data-row-index="${rowIndex}"]`).addClass("kbc-row-highlight");
        }

        $(datatable.wrapper).off("click", ".dt-cell").on("click", ".dt-cell", function(e) {
            highlight_row($(this));
        });

        $(datatable.wrapper).off("click", ".kbc-open").on("click", ".kbc-open", function(e) {
            e.preventDefault();
            e.stopPropagation();
            highlight_row($(this).closest(".dt-cell"));
            show_kbc_popup($(this).data("item"));
        });
    }

    //     // ── inject row-highlight style once ──
    //     if (!$("#kbc-row-highlight-style").length) {
    //         $("<style>")
    //             .attr("id", "kbc-row-highlight-style")
    //             .html(`
    //                 .dt-row.kbc-row-highlight .dt-cell,
    //                 [data-row-index].kbc-row-highlight .dt-cell {
    //                     background-color: #d6e9ff !important;
    //                 }
    //             `)
    //             .appendTo("head");
    //     }

    //     function highlight_row($target) {
    //         const $row = $target.closest(".dt-row, [data-row-index]");
    //         if (!$row.length) return;
    //         $(datatable.wrapper).find(".dt-row, [data-row-index]").removeClass("kbc-row-highlight");
    //         $row.addClass("kbc-row-highlight");
    //     }

    //     // ── click anywhere on a row (any column) → highlight that row ──
    //     $(datatable.wrapper).off("click", ".dt-cell").on("click", ".dt-cell", function(e) {
    //         highlight_row($(this));
    //     });

    //     // ── item code click → open KBC popup AND highlight the row ──
    //     $(datatable.wrapper).off("click", ".kbc-open").on("click", ".kbc-open", function(e) {
    //         e.preventDefault();
    //         e.stopPropagation();
    //         highlight_row($(this));
    //         show_kbc_popup($(this).data("item"));
    //     });
    // }
};


// ─────────────────────────────────────────────────────────────────────────────
// STEP 1 — KBC popup (opens on Item Code click)
// ─────────────────────────────────────────────────────────────────────────────
function show_kbc_popup(base) {

    frappe.dom.freeze(__("Loading KBC stock..."));

    Promise.all([
        kbc_get_bin(base + "K"),
        kbc_get_bin(base + "B"),
        kbc_get_bin(base + "C")
    ]).then(function(results) {

        frappe.dom.unfreeze();

        const k_rows = results[0];
        const b_rows = results[1];
        const c_rows = results[2];

        const k_total = k_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
        const b_total = b_rows.reduce((s, r) => s + flt(r.actual_qty), 0);
        const c_total = c_rows.reduce((s, r) => s + flt(r.actual_qty), 0);

        const warehouses = [];
        [k_rows, b_rows, c_rows].forEach(rows => {
            rows.forEach(r => {
                if (!warehouses.includes(r.warehouse)) warehouses.push(r.warehouse);
            });
        });

        const k_map = kbc_build_map(k_rows);
        const b_map = kbc_build_map(b_rows);
        const c_map = kbc_build_map(c_rows);

        let body = "";
        if (warehouses.length === 0) {
            body = `<tr><td colspan="4" style="text-align:center;padding:14px;color:#999">
                No KBC stock found for ${base}
            </td></tr>`;
        } else {
            warehouses.forEach(wh => {
                const k = flt(k_map[wh] || 0);
                const b = flt(b_map[wh] || 0);
                const c = flt(c_map[wh] || 0);
                if (k === 0 && b === 0 && c === 0) return;
                body += `<tr>
                    <td style="padding:6px 10px">${wh}</td>
                    <td style="padding:6px 10px;text-align:right">
                        ${k > 0
                            ? `<a href="#" class="kbc-drill" data-item="${base}K" data-label="Kalvert"
                                style="color:#1a73e8;font-weight:500">${flt(k,2)}</a>`
                            : `<span style="color:#ccc">—</span>`}
                    </td>
                    <td style="padding:6px 10px;text-align:right">
                        ${b > 0
                            ? `<a href="#" class="kbc-drill" data-item="${base}B" data-label="Buffing"
                                style="color:#e67e22;font-weight:500">${flt(b,2)}</a>`
                            : `<span style="color:#ccc">—</span>`}
                    </td>
                    <td style="padding:6px 10px;text-align:right">
                        ${c > 0
                            ? `<a href="#" class="kbc-drill" data-item="${base}C" data-label="Charak"
                                style="color:#27ae60;font-weight:500">${flt(c,2)}</a>`
                            : `<span style="color:#ccc">—</span>`}
                    </td>
                </tr>`;
            });
        }

        let d = new frappe.ui.Dialog({
            title: __("KBC Stock : " + base),
            size: "large",
            fields: [{ fieldtype: "HTML", fieldname: "kbc_html" }],
            primary_action_label: __("Close"),
            primary_action: function() { d.hide(); }
        });

        d.fields_dict.kbc_html.$wrapper.html(`
            <table class="table table-bordered" style="margin:0;width:100%">
                <thead style="background:#e8f0fe">
                    <tr>
                        <th style="padding:8px 10px">Warehouse</th>
                        <th style="padding:8px 10px;text-align:right;color:#1a73e8">
                            Kalvert<br><small style="font-weight:normal">${base}K</small>
                        </th>
                        <th style="padding:8px 10px;text-align:right;color:#e67e22">
                            Buffing<br><small style="font-weight:normal">${base}B</small>
                        </th>
                        <th style="padding:8px 10px;text-align:right;color:#27ae60">
                            Charak<br><small style="font-weight:normal">${base}C</small>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    ${body}
                    <tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
                        <td style="padding:6px 10px">Total</td>
                        <td style="padding:6px 10px;text-align:right">${flt(k_total,2)}</td>
                        <td style="padding:6px 10px;text-align:right">${flt(b_total,2)}</td>
                        <td style="padding:6px 10px;text-align:right">${flt(c_total,2)}</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin:8px 0 0;font-size:11px;color:#999">
                💡 Click any quantity to see warehouse-wise breakdown &nbsp;|&nbsp;
                <a href="/app/item/${base}" target="_blank" style="color:#2490ef">
                    Open Item Master ↗
                </a>
            </p>
        `);

        d.fields_dict.kbc_html.$wrapper.on("click", ".kbc-drill", function(e) {
            e.preventDefault();
            d.hide();
            show_kbc_drill($(this).data("item"), $(this).data("label"), base);
        });

        d.show();

    }).catch(function(err) {
        frappe.dom.unfreeze();
        console.error("KBC popup error:", err);
        frappe.msgprint({
            title: __("KBC Error"),
            indicator: "red",
            message: __("Error: ") + (err && err.message ? err.message : err)
        });
    });
}


// ─────────────────────────────────────────────────────────────────────────────
// STEP 2 — Warehouse drill-down (click on any K / B / C qty)
// ─────────────────────────────────────────────────────────────────────────────
function show_kbc_drill(item_code, label, base) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Bin",
            filters: { item_code: item_code },
            fields: ["warehouse", "actual_qty"],
            limit_page_length: 50
        },
        callback: function(r) {
            const rows  = r.message || [];
            const total = rows.reduce((s, d) => s + flt(d.actual_qty), 0);

            let body = "";
            if (rows.length) {
                rows.forEach(d => {
                    body += `<tr>
                        <td style="padding:6px 10px">${d.warehouse}</td>
                        <td style="padding:6px 10px;text-align:right;font-weight:500">
                            ${flt(d.actual_qty, 2)}
                        </td>
                    </tr>`;
                });
                body += `<tr style="border-top:2px solid #aaa;font-weight:bold;background:#f8f8f8">
                    <td style="padding:6px 10px">Total</td>
                    <td style="padding:6px 10px;text-align:right">${flt(total,2)}</td>
                </tr>`;
            } else {
                body = `<tr><td colspan="2" style="text-align:center;padding:12px;color:#999">
                    No stock found
                </td></tr>`;
            }

            let d2 = new frappe.ui.Dialog({
                title: __(`${label} Warehouse Stock : ${item_code}`),
                fields: [{ fieldtype: "HTML", fieldname: "wh_html" }],
                primary_action_label: __("Close"),
                primary_action: function() { d2.hide(); },
                secondary_action_label: __("← Back to KBC"),
                secondary_action: function() {
                    d2.hide();
                    show_kbc_popup(base);
                }
            });

            d2.fields_dict.wh_html.$wrapper.html(`
                <table class="table table-bordered" style="margin:0;width:100%">
                    <thead style="background:#f0f4f8">
                        <tr>
                            <th style="padding:8px 10px">Warehouse</th>
                            <th style="padding:8px 10px;text-align:right">Qty</th>
                        </tr>
                    </thead>
                    <tbody>${body}</tbody>
                </table>
            `);

            d2.show();
        }
    });
}


// ── Helpers ──────────────────────────────────────────────────────────────────
function kbc_get_bin(item_code) {
    return new Promise(function(resolve) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Bin",
                filters: { item_code: item_code },
                fields: ["warehouse", "actual_qty"],
                limit_page_length: 50
            },
            callback: function(r) { resolve(r.message || []); },
            error: function() { resolve([]); }
        });
    });
}

function kbc_build_map(rows) {
    const map = {};
    rows.forEach(r => { map[r.warehouse] = flt(r.actual_qty); });
    return map;
}