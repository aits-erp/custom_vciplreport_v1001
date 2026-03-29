import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def validate_filters(filters):
    if filters.get("from_date") and filters.get("to_date"):
        if date_diff(filters.to_date, filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))


def get_data(filters):

    conditions = ""

    if filters.get("company"):
        conditions += " AND po.company = %(company)s"

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    suppliers = frappe.db.sql(f"""
        SELECT
            s.name,
            s.supplier_name AS party,
            COUNT(DISTINCT po.name) AS order_count,
            SUM(poi.qty) AS qty,
            SUM(poi.received_qty) AS received_qty,
            SUM(poi.qty - poi.received_qty) AS pending_qty
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        INNER JOIN `tabSupplier` s ON s.name = po.supplier
        WHERE po.docstatus = 1
        AND po.status NOT IN ('Completed','Closed','Stopped','On Hold')
        {conditions}
        GROUP BY s.name
    """, filters, as_dict=True)

    final = []

    for row in suppliers:

        row.fill_ratio = round(
            (flt(row.received_qty) / flt(row.qty) * 100)
            if row.qty else 0,
            2
        )

        if row.fill_ratio < 50:
            row.risk = "Critical"
        elif row.fill_ratio < 80:
            row.risk = "Warning"
        else:
            row.risk = "OK"

        row.order_popup = frappe.as_json(get_supplier_orders(row.name))
        final.append(row)

    return final


def get_supplier_orders(supplier):

    orders = frappe.db.sql("""
        SELECT
            po.name AS po_no,
            po.transaction_date AS po_date,
            SUM(poi.qty) AS qty,
            SUM(poi.received_qty) AS received,
            SUM(poi.qty - poi.received_qty) AS pending
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE po.supplier = %s
        AND po.docstatus = 1
        AND po.status NOT IN ('Completed','Closed','Stopped','On Hold')
        GROUP BY po.name
        HAVING pending > 0
    """, supplier, as_dict=True)

    for o in orders:
        o.fill_ratio = round(
            (flt(o.received) / flt(o.qty) * 100)
            if o.qty else 0,
            2
        )
        o.pending_popup = frappe.as_json(get_pending_items(o.po_no))

    return orders


def get_pending_items(po):

    return frappe.db.sql("""
        SELECT
            item_name AS item,
            qty,
            received_qty AS received,
            (qty - received_qty) AS pending
        FROM `tabPurchase Order Item`
        WHERE parent = %s
        AND qty > received_qty
    """, po, as_dict=True)


def get_columns():

    return [
        {"label": _("Supplier"), "fieldname": "party", "width": 260},
        {"label": _("PO Count"), "fieldname": "order_count", "fieldtype": "Int", "width": 120},
        {"label": _("Total Ordered"), "fieldname": "qty", "fieldtype": "Float"},
        {"label": _("Received"), "fieldname": "received_qty", "fieldtype": "Float"},
        {"label": _("Pending"), "fieldname": "pending_qty", "fieldtype": "Float"},
        {"label": _("Fill %"), "fieldname": "fill_ratio", "fieldtype": "Percent"},
        {"label": _("Risk Level"), "fieldname": "risk", "width": 120},
        {"fieldname": "order_popup", "hidden": 1},
    ]
