import copy
import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    if not filters:
        return [], [], None, []

    validate_filters(filters)

    columns = get_columns(filters)
    conditions = get_conditions(filters)
    data = get_data(conditions, filters)

    if not data:
        return columns, [], None, []

    data, chart_data, totals = prepare_data(data, filters)

    report_summary = [
        {"label": _("Ordered Qty"), "value": totals["qty"], "datatype": "Float"},
        {"label": _("Delivered Qty"), "value": totals["delivered_qty"], "datatype": "Float"},
        {"label": _("Pending Qty"), "value": totals["pending_qty"], "datatype": "Float"},
    ]

    return columns, data, None, chart_data, report_summary


# ---------------- VALIDATION ----------------

def validate_filters(filters):
    if filters.get("from_date") and filters.get("to_date"):
        if date_diff(filters.to_date, filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))


# ---------------- CONDITIONS ----------------

def get_conditions(filters):

    conditions = ""

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("company"):
        conditions += " AND so.company = %(company)s"

    if filters.get("sales_order"):
        conditions += " AND so.name IN %(sales_order)s"

    if filters.get("warehouse"):
        conditions += " AND soi.warehouse = %(warehouse)s"

    return conditions


# ---------------- DATA ----------------

def get_data(conditions, filters):

    data = frappe.db.sql(f"""
        SELECT
            so.transaction_date AS date,
            so.name AS sales_order,
            so.status,
            c.customer_name AS customer,
            soi.item_code,
            soi.item_name,
            soi.qty,
            soi.delivered_qty,
            (soi.qty - soi.delivered_qty) AS pending_qty,
            soi.delivery_date,
            soi.warehouse
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        INNER JOIN `tabCustomer` c ON c.name = so.customer
        WHERE so.docstatus = 1
        AND so.status NOT IN ('Completed','Closed','Stopped','On Hold')
        {conditions}
    """, filters, as_dict=True)

    bins = frappe.db.sql("""
        SELECT item_code, warehouse, actual_qty
        FROM `tabBin`
    """, as_dict=True)

    bin_map = {(b.item_code, b.warehouse): b.actual_qty for b in bins}

    so_popup = {}

    for row in data:

        available = bin_map.get((row.item_code, row.warehouse), 0)

        ratio = (row.delivered_qty / row.qty * 100) if row.qty > 0 else 0
        row["fill_ratio"] = round(ratio, 2)

        so_popup.setdefault(row.sales_order, {
            "items": [],
            "totals": {"ordered": 0, "delivered": 0, "pending": 0}
        })

        so_popup[row.sales_order]["items"].append({
            "item_name": row.item_name,
            "ordered_qty": row.qty,
            "delivered_qty": row.delivered_qty,
            "pending_qty": row.pending_qty,
            "available_qty": available,
            "ratio": round(ratio, 2),
            "delivery_date": str(row.delivery_date) if row.delivery_date else ""
        })

        so_popup[row.sales_order]["totals"]["ordered"] += flt(row.qty)
        so_popup[row.sales_order]["totals"]["delivered"] += flt(row.delivered_qty)
        so_popup[row.sales_order]["totals"]["pending"] += flt(row.pending_qty)

    for row in data:
        row["pending_popup"] = frappe.as_json(so_popup.get(row.sales_order, {}))

    return data


# ---------------- PREPARE ----------------

def prepare_data(data, filters):

    sales_order_map = {}

    totals = {"qty": 0, "delivered_qty": 0, "pending_qty": 0}

    for row in data:

        totals["qty"] += flt(row.qty)
        totals["delivered_qty"] += flt(row.delivered_qty)
        totals["pending_qty"] += flt(row.pending_qty)

        if filters.get("group_by_so"):

            so = row.sales_order

            if so not in sales_order_map:
                sales_order_map[so] = copy.deepcopy(row)
            else:
                sales_order_map[so].qty += flt(row.qty)
                sales_order_map[so].delivered_qty += flt(row.delivered_qty)
                sales_order_map[so].pending_qty += flt(row.pending_qty)

    for so in sales_order_map.values():
        so.fill_ratio = round(
            (so.delivered_qty / so.qty * 100) if so.qty > 0 else 0, 2
        )

    chart_data = {
        "data": {
            "labels": [_("Pending Qty"), _("Delivered Qty")],
            "datasets": [{"values": [totals["pending_qty"], totals["delivered_qty"]]}],
        },
        "type": "donut",
        "height": 300,
    }

    if filters.get("group_by_so"):
        return list(sales_order_map.values()), chart_data, totals

    return data, chart_data, totals


# ---------------- COLUMNS ----------------

def get_columns(filters):

    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date"},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order"},
        {"label": _("Pending Delivery"), "fieldname": "pending_delivery"},
        {"label": _("Customer"), "fieldname": "customer"},

        {"label": _("Ordered Qty"), "fieldname": "qty", "fieldtype": "Float"},
        {"label": _("Delivered Qty"), "fieldname": "delivered_qty", "fieldtype": "Float"},
        {"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float"},
        {"label": _("Fill Ratio %"), "fieldname": "fill_ratio", "fieldtype": "Float"},

        {"fieldname": "pending_popup", "hidden": 1},
    ]
