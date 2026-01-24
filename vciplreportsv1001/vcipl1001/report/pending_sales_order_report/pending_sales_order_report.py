# Copyright (c)
# For license information, please see license.txt

import copy
from collections import OrderedDict

import frappe
from frappe import _, qb
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Max
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	if not filters:
		return [], [], None, []

	validate_filters(filters)

	columns = get_columns(filters)
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)
	so_elapsed_time = get_so_elapsed_time(data)

	if not data:
		return columns, [], None, []

	data, chart_data, totals = prepare_data(data, so_elapsed_time, filters)

	# 🔥 FOOTER TOTALS
	report_summary = [
		{"label": _("Delivered Qty"), "value": totals["delivered_qty"], "datatype": "Float"},
		{"label": _("Qty to Deliver"), "value": totals["pending_qty"], "datatype": "Float"},
		{"label": _("Billed Qty"), "value": totals["billed_qty"], "datatype": "Float"},
		{"label": _("Qty to Bill"), "value": totals["qty_to_bill"], "datatype": "Float"},
		{"label": _("Amount"), "value": totals["amount"], "datatype": "Currency"},
		{"label": _("Billed Amount"), "value": totals["billed_amount"], "datatype": "Currency"},
		{"label": _("Pending Amount"), "value": totals["pending_amount"], "datatype": "Currency"},
		{"label": _("Amount Delivered"), "value": totals["delivered_qty_amount"], "datatype": "Currency"},
	]

	return columns, data, None, chart_data, report_summary


# --------------------------------------------------
# VALIDATIONS
# --------------------------------------------------
def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")

	if not from_date and to_date:
		frappe.throw(_("From and To Dates are required."))
	elif from_date and to_date and date_diff(to_date, from_date) < 0:
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
# DATA QUERY
# --------------------------------------------------
def get_data(conditions, filters):
	return frappe.db.sql(
		f"""
		SELECT
			so.transaction_date AS date,
			soi.delivery_date AS delivery_date,
			so.name AS sales_order,
			so.status,
			so.customer,
			soi.item_code,
			DATEDIFF(CURRENT_DATE, soi.delivery_date) AS delay,
			soi.qty,
			soi.delivered_qty,
			(soi.qty - soi.delivered_qty) AS pending_qty,
			IFNULL(SUM(sii.qty), 0) AS billed_qty,
			soi.base_amount AS amount,
			(soi.delivered_qty * soi.base_rate) AS delivered_qty_amount,
			(soi.billed_amt * IFNULL(so.conversion_rate, 1)) AS billed_amount,
			(soi.base_amount - (soi.billed_amt * IFNULL(so.conversion_rate, 1))) AS pending_amount,
			soi.warehouse,
			so.company,
			soi.name,
			soi.description
		FROM `tabSales Order` so
		INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
		LEFT JOIN `tabSales Invoice Item` sii
			ON sii.so_detail = soi.name AND sii.docstatus = 1
		WHERE
			so.docstatus = 1
			AND so.status NOT IN ('Stopped', 'On Hold')
			{conditions}
		GROUP BY soi.name
		ORDER BY so.transaction_date ASC
		""",
		filters,
		as_dict=True,
	)


# --------------------------------------------------
# ELAPSED TIME
# --------------------------------------------------
def get_so_elapsed_time(data):
	so_elapsed_time = OrderedDict()
	if not data:
		return so_elapsed_time

	sales_orders = list({d.sales_order for d in data})

	so = qb.DocType("Sales Order")
	soi = qb.DocType("Sales Order Item")
	dn = qb.DocType("Delivery Note")
	dni = qb.DocType("Delivery Note Item")

	to_seconds = CustomFunction("TO_SECONDS", ["date"])

	query = (
		qb.from_(so)
		.inner_join(soi).on(soi.parent == so.name)
		.left_join(dni).on(dni.so_detail == soi.name)
		.left_join(dn).on(dni.parent == dn.name)
		.select(
			so.name.as_("sales_order"),
			soi.item_code.as_("item_code"),
			(to_seconds(Max(dn.posting_date)) - to_seconds(so.transaction_date)).as_("elapsed_seconds"),
		)
		.where((so.name.isin(sales_orders)) & (dn.docstatus == 1))
		.groupby(soi.name)
	)

	for r in query.run(as_dict=True):
		so_elapsed_time[(r.sales_order, r.item_code)] = r.elapsed_seconds

	return so_elapsed_time


# --------------------------------------------------
# PREPARE DATA + TOTALS
# --------------------------------------------------
def prepare_data(data, so_elapsed_time, filters):
	sales_order_map = {}

	totals = {
		"delivered_qty": 0,
		"pending_qty": 0,
		"billed_qty": 0,
		"qty_to_bill": 0,
		"amount": 0,
		"billed_amount": 0,
		"pending_amount": 0,
		"delivered_qty_amount": 0,
	}

	for row in data:
		row.qty_to_bill = flt(row.qty) - flt(row.billed_qty)
		row.delay = 0 if row.delay and row.delay < 0 else row.delay
		row.time_taken_to_deliver = (
			so_elapsed_time.get((row.sales_order, row.item_code))
			if row.status in ("Completed", "To Bill")
			else 0
		)

		for f in totals:
			totals[f] += flt(row.get(f))

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
				so_row.delivery_date = max(getdate(so_row.delivery_date), getdate(row.delivery_date))
				for f in totals:
					so_row[f] = flt(so_row.get(f)) + flt(row.get(f))

	chart_data = prepare_chart_data(totals["pending_amount"], totals["billed_amount"])

	if filters.get("group_by_so"):
		return list(sales_order_map.values()), chart_data, totals

	return data, chart_data, totals


# --------------------------------------------------
# CHART
# --------------------------------------------------
def prepare_chart_data(pending, completed):
	return {
		"data": {
			"labels": [_("Amount to Bill"), _("Billed Amount")],
			"datasets": [{"values": [pending, completed]}],
		},
		"type": "donut",
		"height": 300,
	}


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns(filters):
	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 90},
		{"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 160},
		{"label": _("Status"), "fieldname": "status", "width": 120},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
	]

	if not filters.get("group_by_so"):
		columns.extend([
			{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
			{"label": _("Description"), "fieldname": "description", "width": 150},
		])

	columns.extend([
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
		{"label": _("Delivered Qty"), "fieldname": "delivered_qty", "fieldtype": "Float", "width": 120},
		{"label": _("Qty to Deliver"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 120},
		{"label": _("Billed Qty"), "fieldname": "billed_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Qty to Bill"), "fieldname": "qty_to_bill", "fieldtype": "Float", "width": 100},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120, "options": "Company:company:default_currency"},
		{"label": _("Billed Amount"), "fieldname": "billed_amount", "fieldtype": "Currency", "width": 120, "options": "Company:company:default_currency"},
		{"label": _("Pending Amount"), "fieldname": "pending_amount", "fieldtype": "Currency", "width": 120, "options": "Company:company:default_currency"},
		{"label": _("Amount Delivered"), "fieldname": "delivered_qty_amount", "fieldtype": "Currency", "width": 120, "options": "Company:company:default_currency"},
		{"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 120},
		{"label": _("Delay (Days)"), "fieldname": "delay", "width": 100},
		{"label": _("Time Taken to Deliver"), "fieldname": "time_taken_to_deliver", "fieldtype": "Duration", "width": 120},
	])

	if not filters.get("group_by_so"):
		columns.append({"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120})

	columns.append({"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120})

	return columns
