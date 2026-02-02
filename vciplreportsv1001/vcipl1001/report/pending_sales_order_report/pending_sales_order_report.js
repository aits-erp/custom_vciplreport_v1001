// frappe.query_reports["Pending Sales Order Report"] = {
// 	filters: [
// 		{
// 			fieldname: "company",
// 			label: __("Company"),
// 			fieldtype: "Link",
// 			options: "Company",
// 			default: frappe.defaults.get_user_default("Company"),
// 			reqd: 1
// 		},
// 		{
// 			fieldname: "from_date",
// 			label: __("From Date"),
// 			fieldtype: "Date"
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: __("To Date"),
// 			fieldtype: "Date"
// 		},
// 		{
// 			fieldname: "sales_order",
// 			label: __("Sales Order"),
// 			fieldtype: "MultiSelectList",
// 			options: "Sales Order",
// 			get_data(txt) {
// 				return frappe.db.get_link_options("Sales Order", txt);
// 			}
// 		},
// 		{
// 			fieldname: "customer",
// 			label: __("Customer"),
// 			fieldtype: "Link",
// 			options: "Customer"
// 		},
// 		{
// 			fieldname: "status",
// 			label: __("Status"),
// 			fieldtype: "MultiSelectList",
// 			options: ["Draft", "To Deliver", "To Bill"]
// 		},
// 		{
// 			fieldname: "warehouse",
// 			label: __("Warehouse"),
// 			fieldtype: "Link",
// 			options: "Warehouse"
// 		},
// 		{
// 			fieldname: "group_by_so",
// 			label: __("Group by Sales Order"),
// 			fieldtype: "Check",
// 			default: 1
// 		}
// 	],

// 	formatter(value, row, column, data, default_formatter) {
// 		value = default_formatter(value, row, column, data);

// 		if (column.fieldname === "pending_qty" && data?.pending_qty > 0) {
// 			value = `<span style="color:#d9534f;font-weight:600">${value}</span>`;
// 		}

// 		return value;
// 	},

// 	onload(report) {
// 		report.page.add_inner_button(__("Group by Sales Order"), () => {
// 			report.set_filter_value("group_by_so", 1);
// 			report.refresh();
// 		});

// 		report.page.add_inner_button(__("Item Wise"), () => {
// 			report.set_filter_value("group_by_so", 0);
// 			report.refresh();
// 		});
// 	}
// };
frappe.query_reports["Pending Sales Order Report"] = {

	filters: [
		{ fieldname:"company", label:"Company", fieldtype:"Link", options:"Company", default:frappe.defaults.get_user_default("Company"), reqd:1 },
		{ fieldname:"from_date", label:"From Date", fieldtype:"Date" },
		{ fieldname:"to_date", label:"To Date", fieldtype:"Date" },
		{ fieldname:"group_by_so", label:"Group by Sales Order", fieldtype:"Check", default:1 }
	],

	formatter(value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		if (column.fieldname === "pending_qty" && data.pending_qty > 0) {
			value = `<span style="color:red;font-weight:600">${value}</span>`;
		}

		if (column.fieldname === "pending_delivery") {
			return `<a style="font-weight:bold;color:#1674E0;cursor:pointer"
				onclick='frappe.query_reports["Pending Sales Order Report"]
				.show_popup(${data.pending_popup})'>
				View Pending
			</a>`;
		}

		return value;
	},

	show_popup(rows) {

		if (!rows || rows.length === 0) {
			frappe.msgprint("No pending items");
			return;
		}

		let html = `
		<div style="max-height:450px;overflow:auto">
		<table class="table table-bordered">
		<tr>
			<th>Item</th><th>Qty</th><th>Delivered</th><th>Pending</th><th>Date</th>
		</tr>`;

		rows.forEach(r=>{
			html+=`<tr>
				<td>${r.item_code}</td>
				<td>${r.qty}</td>
				<td>${r.delivered_qty}</td>
				<td style="color:red;font-weight:bold">${r.pending_qty}</td>
				<td>${r.delivery_date}</td>
			</tr>`;
		});

		html += "</table></div>";

		frappe.msgprint({title:"Pending Items", message:html, wide:true});
	}
};
