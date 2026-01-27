frappe.query_reports["Sales Order Pending Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "sales_order",
			label: __("Sales Order"),
			fieldtype: "MultiSelectList",
			options: "Sales Order",
			get_data: function (txt) {
				return frappe.db.get_link_options("Sales Order", txt);
			}
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "MultiSelectList",
			options: [
				"Draft",
				"To Deliver and Bill",
				"To Deliver",
				"To Bill",
				"Completed",
				"Closed"
			]
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse"
		},
		{
			fieldname: "group_by_so",
			label: __("Group by Sales Order"),
			fieldtype: "Check",
			default: 0
		}
	]
};
