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
			fieldname: "group_by_so",
			label: __("Group by Sales Order"),
			fieldtype: "Check",
			default: 1
		}
	],

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "pending_qty" && data?.pending_qty > 0) {
			value = `<span style="color:#d9534f;font-weight:600">${value}</span>`;
		}

		if (column.fieldname === "pending_delivery" && data?.sales_order) {
			value = `
				<button class="btn btn-xs btn-primary pending-delivery-btn"
					data-so="${data.sales_order}">
					View Pending
				</button>`;
		}

		return value;
	},

	onload(report) {

		report.page.add_inner_button(__("Group by Sales Order"), () => {
			report.set_filter_value("group_by_so", 1);
			report.refresh();
		});

		report.page.add_inner_button(__("Item Wise"), () => {
			report.set_filter_value("group_by_so", 0);
			report.refresh();
		});
	}
};


// --------------------------------------------------
// POPUP DIALOG
// --------------------------------------------------
frappe.query_reports["Pending Sales Order Report"].show_pending_dialog = function(so) {

	frappe.call({
		method: "vciplreportsv1001.vciplreportsv1001.report.pending_sales_order_report.pending_sales_order_report.get_pending_delivery_items",

		args: { sales_order: so },
		callback: function(r) {

			let data = r.message || [];

			let dialog = new frappe.ui.Dialog({
				title: "Pending Delivery - " + so,
				size: "large",
				fields: [{ fieldtype: "HTML", fieldname: "table" }]
			});

			let html = `
				<div style="max-height:400px;overflow:auto">
				<table class="table table-bordered table-hover">
				<thead>
					<tr>
						<th>Item Code</th>
						<th>Item Name</th>
						<th>Qty</th>
						<th>Delivered</th>
						<th style="color:red">Pending</th>
						<th>Delivery Date</th>
					</tr>
				</thead>
				<tbody>
			`;

			data.forEach(d => {
				html += `
					<tr>
						<td>${d.item_code}</td>
						<td>${d.item_name || ""}</td>
						<td>${d.qty}</td>
						<td>${d.delivered_qty}</td>
						<td style="color:#d9534f;font-weight:600">${d.pending_qty}</td>
						<td>${d.delivery_date || ""}</td>
					</tr>`;
			});

			html += "</tbody></table></div>";

			dialog.fields_dict.table.$wrapper.html(html);
			dialog.show();
		}
	});
};


// click event
$(document).on("click", ".pending-delivery-btn", function() {
	let so = $(this).data("so");
	frappe.query_reports["Pending Sales Order Report"].show_pending_dialog(so);
});
