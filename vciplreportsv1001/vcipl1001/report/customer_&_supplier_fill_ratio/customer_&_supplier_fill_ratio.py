import copy
import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    if not filters:
        return [], [], None, []

    validate_filters(filters)

    columns = get_columns()
    conditions = get_conditions(filters)
    data = get_data(conditions, filters)

    if not data:
        return columns, [], None, []

    data, chart_data, totals = prepare_data(data)

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
        conditions += " AND transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("company"):
        conditions += " AND company = %(company)s"

    return conditions


# ---------------- DATA ----------------

def get_data(conditions, filters):

    party_type = filters.get("party_type", "Both")
    queries = []

    if party_type in ["Both", "Customer"]:
        queries.append(f"""
            SELECT
                'Customer' AS party_type,
                so.transaction_date AS date,
                so.name AS order_id,
                c.customer_name AS party,
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
        """)

    if party_type in ["Both", "Supplier"]:
        queries.append(f"""
            SELECT
                'Supplier' AS party_type,
                po.transaction_date AS date,
                po.name AS order_id,
                s.supplier_name AS party,
                poi.item_code,
                poi.item_name,
                poi.qty,
                poi.received_qty AS delivered_qty,
                (poi.qty - poi.received_qty) AS pending_qty,
                poi.schedule_date AS delivery_date,
                poi.warehouse
            FROM `tabPurchase Order` po
            INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
            INNER JOIN `tabSupplier` s ON s.name = po.supplier
            WHERE po.docstatus = 1
            AND po.status NOT IN ('Completed','Closed','Stopped')
            {conditions}
        """)

    data = frappe.db.sql(" UNION ALL ".join(queries), filters, as_dict=True)

    bins = frappe.db.sql("""
        SELECT item_code, warehouse, actual_qty
        FROM `tabBin`
    """, as_dict=True)

    bin_map = {(b.item_code, b.warehouse): b.actual_qty for b in bins}

    popup_map = {}

    for row in data:

        available = bin_map.get((row.item_code, row.warehouse), 0)
        ratio = (row.delivered_qty / row.qty * 100) if row.qty else 0
        row["fill_ratio"] = round(ratio, 2)

        popup_map.setdefault(row.order_id, {
            "items": [],
            "totals": {"ordered": 0, "delivered": 0, "pending": 0}
        })

        popup_map[row.order_id]["items"].append({
            "item_name": row.item_name,
            "ordered_qty": row.qty,
            "delivered_qty": row.delivered_qty,
            "pending_qty": row.pending_qty,
            "available_qty": available,
            "ratio": round(ratio, 2),
            "delivery_date": str(row.delivery_date or "")
        })

        popup_map[row.order_id]["totals"]["ordered"] += flt(row.qty)
        popup_map[row.order_id]["totals"]["delivered"] += flt(row.delivered_qty)
        popup_map[row.order_id]["totals"]["pending"] += flt(row.pending_qty)

    for row in data:
        row["pending_popup"] = frappe.as_json(popup_map.get(row.order_id, {}))

    return data


# ---------------- PREPARE ----------------

def prepare_data(data):

    totals = {"qty": 0, "delivered_qty": 0, "pending_qty": 0}
    order_map = {}

    for row in data:

        totals["qty"] += flt(row.qty)
        totals["delivered_qty"] += flt(row.delivered_qty)
        totals["pending_qty"] += flt(row.pending_qty)

        if row.order_id not in order_map:
            order_map[row.order_id] = copy.deepcopy(row)
        else:
            order_map[row.order_id].qty += flt(row.qty)
            order_map[row.order_id].delivered_qty += flt(row.delivered_qty)
            order_map[row.order_id].pending_qty += flt(row.pending_qty)

    for so in order_map.values():
        so.fill_ratio = round((so.delivered_qty / so.qty * 100) if so.qty else 0, 2)

    chart_data = {
        "data": {
            "labels": [_("Pending Qty"), _("Delivered Qty")],
            "datasets": [{"values": [totals["pending_qty"], totals["delivered_qty"]]}],
        },
        "type": "donut",
        "height": 300,
    }

    return list(order_map.values()), chart_data, totals


# ---------------- COLUMNS ----------------

def get_columns():

    return [
        {"label": _("Party Type"), "fieldname": "party_type"},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date"},
        {"label": _("Order"), "fieldname": "order_id"},
        {"label": _("Party"), "fieldname": "party"},
        {"label": _("Pending Delivery"), "fieldname": "pending_delivery"},
        {"label": _("Ordered Qty"), "fieldname": "qty", "fieldtype": "Float"},
        {"label": _("Delivered Qty"), "fieldname": "delivered_qty", "fieldtype": "Float"},
        {"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float"},
        {"label": _("Fill Ratio %"), "fieldname": "fill_ratio", "fieldtype": "Float"},
        {"fieldname": "pending_popup", "hidden": 1},
    ]
