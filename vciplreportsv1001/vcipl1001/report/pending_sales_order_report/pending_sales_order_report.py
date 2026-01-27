import copy
from collections import OrderedDict

import frappe
from frappe import _, qb
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Max
from frappe.utils import flt, getdate, date_diff


# --------------------------------------------------
# EXECUTE
# --------------------------------------------------
def execute(filters=None):
	if not filters:
		return [], [], None, []

	validate_filters(filters)

	columns = get_columns(filters)
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)

	# 🔧 ERROR FIX: function now exists
	so_elapsed_time = get_so_elapsed_time(data)

	if not data:
		return columns, [], None, []

	data, chart_data, totals = prepare_data(data, so_elapsed_time, filters)

	report_summary = [
		{"label": _("Ordered Qty"), "value": totals["qty"], "datatype": "Float"},
		{"label": _("Delivered Qty"), "value": totals["delivered_qty"], "datatype": "Float"},
		{"label": _("Qty to Deliver"), "value": totals["pending_qty"], "datatype": "Float"},
		{"label": _("Order Amount"), "value": totals["amount"], "datatype": "Currency"},
		{"label": _("Delivered Amount"), "value": totals["delivered_qty_amount"], "datatype": "Currency"},
		{"label": _("Pending Amount"), "value": totals["pending_amount"], "datatype": "Currency"},
	]

	return columns, data, None, chart_data, report_summary


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------
def validate_filters(filters):
	if filters.get("from_date") and filters.get("to_date"):
		if date_diff(filters.to_date, filters.from_date) < 0:
			frappe.throw(_("To Date cannot be before From Date."))


# --------------------------------------------------
# CONDITIONS
# --------------------------------------------------
def get_conditions(filters):
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and so.transaction_date between %(from_date)s and %(to_date)s"

	if filters.get("company"):
		conditions += " and so.company = %(company)s"

	if filters.get("sales_order"):
		conditions += " and so.name in %(sales_order)s"

	if filters.get("status"):
		conditions += " and so.status in %(status)s"

	if filters.get("warehouse"):
		conditions += " and soi.warehouse = %(warehouse)s"

	return conditions


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(conditions, filters):
	return frappe.db.sql(
		f"""
		SELECT
			so.transaction_date AS date,
			soi.delivery_date,
			so.name AS sales_order,
			so.status,
			c.customer_name AS customer,
			soi.item_code,
			soi.qty,
			soi.delivered_qty,
			(soi.qty - soi.delivered_qty) AS pending_qty,
			soi.base_amount AS amount,
			(soi.delivered_qty * soi.base_rate) AS delivered_qty_amount,
			(soi.base_amount - (soi.delivered_qty * soi.base_rate)) AS pending_amount,
			soi.warehouse,
			soi.description
		FROM `tabSales Order` so
		INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
		INNER JOIN `tabCustomer` c ON c.name = so.customer
		WHERE so.docstatus = 1
		AND so.status NOT IN ('Stopped', 'On Hold')
		{conditions}
		ORDER BY so.transaction_date
		""",
		filters,
		as_dict=True
	)


# --------------------------------------------------
# 🔧 ERROR FIX: DUMMY FUNCTION (OLD LOGIC SAFE)
# --------------------------------------------------
def get_so_elapsed_time(data):
	"""
	This function existed in old logic.
	It is kept to avoid NameError.
	Currently not used for calculations.
	"""
	return {}


# --------------------------------------------------
# PREPARE DATA (OLD LOGIC)
# --------------------------------------------------
def prepare_data(data, so_elapsed_time, filters):
	sales_order_map = {}
	totals = {
		"qty": 0,
		"delivered_qty": 0,
		"pending_qty": 0,
		"amount": 0,
		"delivered_qty_amount": 0,
		"pending_amount": 0,
	}

	for row in data:
		totals["qty"] += flt(row.qty)
		totals["delivered_qty"] += flt(row.delivered_qty)
		totals["pending_qty"] += flt(row.pending_qty)
		totals["amount"] += flt(row.amount)
		totals["delivered_qty_amount"] += flt(row.delivered_qty_amount)
		totals["pending_amount"] += flt(row.pending_amount)

		if filters.get("group_by_so"):
			so = row.sales_order
			if so not in sales_order_map:
				so_row = copy.deepcopy(row)
				so_row.item_code = ""
				so_row.description = ""
				so_row.warehouse = ""
				sales_order_map[so] = so_row
			else:
				so_row = sales_order_map[so]
				so_row.qty += flt(row.qty)
				so_row.delivered_qty += flt(row.delivered_qty)
				so_row.pending_qty += flt(row.pending_qty)
				so_row.amount += flt(row.amount)
				so_row.delivered_qty_amount += flt(row.delivered_qty_amount)
				so_row.pending_amount += flt(row.pending_amount)
				so_row.delivery_date = max(
					getdate(so_row.delivery_date),
					getdate(row.delivery_date)
				)

	chart_data = prepare_chart_data(
		totals["pending_amount"],
		totals["delivered_qty_amount"]
	)

	if filters.get("group_by_so"):
		return list(sales_order_map.values()), chart_data, totals

	return data, chart_data, totals


# --------------------------------------------------
# CHART
# --------------------------------------------------
def prepare_chart_data(pending, delivered):
	return {
		"data": {
			"labels": [_("Pending Amount"), _("Delivered Amount")],
			"datasets": [{"values": [pending, delivered]}],
		},
		"type": "donut",
		"height": 300,
	}


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns(filters):
	qty_label = _("Ordered Qty") if filters.get("group_by_so") else _("Qty")

	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date"},
		{"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order"},
		{"label": _("Status"), "fieldname": "status"},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Data"},
		{"label": qty_label, "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("Delivered Qty"), "fieldname": "delivered_qty", "fieldtype": "Float"},
		{"label": _("Qty to Deliver"), "fieldname": "pending_qty", "fieldtype": "Float"},
		{"label": _("Order Amount"), "fieldname": "amount", "fieldtype": "Currency"},
		{"label": _("Delivered Amount"), "fieldname": "delivered_qty_amount", "fieldtype": "Currency"},
		{"label": _("Pending Amount"), "fieldname": "pending_amount", "fieldtype": "Currency"},
	]

	return columns
