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

//         // 🚀 FORCE ONLY ITEM CODE (NO ITEM NAME)
//         if (column.fieldname === "item_code") {
//             return `<a href="/app/item/${value}" target="_blank">${value}</a>`;
//         }

//         return default_formatter(value, row, column, data);
//     }
// };

// //changes

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
        // FOR ITEM CODE + NAME COLUMN
        if (column.fieldname === "item_code_name") {
            if (data && data.item_code && data.item_name) {
                return `<a href="/app/item/${data.item_code}" target="_blank">${data.item_code} - ${data.item_name}</a>`;
            }
            return value;
        }

        // FORCE ONLY ITEM CODE (NO ITEM NAME)
        if (column.fieldname === "item_code") {
            return `<a href="/app/item/${value}" target="_blank">${value}</a>`;
        }

        return default_formatter(value, row, column, data);
    }
};