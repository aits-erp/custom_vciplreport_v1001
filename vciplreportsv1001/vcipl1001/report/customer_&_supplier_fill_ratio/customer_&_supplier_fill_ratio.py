import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# ---------------- VALIDATION ----------------

def validate_filters(filters):
    if filters.get("from_date") and filters.get("to_date"):
        if date_diff(filters.to_date, filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))


# ---------------- DATA ----------------

def get_data(filters):

    conditions = ""

    if filters.get("company"):
        conditions += " AND company = %(company)s"

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    party_type = filters.get("party_type", "Both")
    queries = []

    # ---------- CUSTOMER ----------
    if party_type in ["Both", "Customer"]:
        queries.append(f"""
            SELECT
                'Customer' AS party_type,
                c.customer_name AS party,
                COUNT(DISTINCT so.name) AS order_count,
                SUM(soi.qty) AS qty,
                SUM(soi.delivered_qty) AS delivered_qty,
                SUM(soi.qty - soi.delivered_qty) AS pending_qty
            FROM `tabSales Order` so
            INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
            INNER JOIN `tabCustomer` c ON c.name = so.customer
            WHERE so.docstatus = 1
            AND so.status NOT IN ('Completed','Closed','Stopped','On Hold')
            {conditions}
            GROUP BY c.customer_name
        """)

    # ---------- SUPPLIER ----------
    if party_type in ["Both", "Supplier"]:
        queries.append(f"""
            SELECT
                'Supplier' AS party_type,
                s.supplier_name AS party,
                COUNT(DISTINCT po.name) AS order_count,
                SUM(poi.qty) AS qty,
                SUM(poi.received_qty) AS delivered_qty,
                SUM(poi.qty - poi.received_qty) AS pending_qty
            FROM `tabPurchase Order` po
            INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
            INNER JOIN `tabSupplier` s ON s.name = po.supplier
            WHERE po.docstatus = 1
            AND po.status NOT IN ('Completed','Closed','Stopped')
            {conditions}
            GROUP BY s.supplier_name
        """)

    raw = frappe.db.sql(" UNION ALL ".join(queries), filters, as_dict=True)

    final = []

    for row in raw:

        # fill ratio
        row.fill_ratio = round(
            (flt(row.delivered_qty) / flt(row.qty) * 100)
            if row.qty else 0,
            2
        )

        # risk classification
        if row.fill_ratio < 50:
            row.risk = "Critical"
        elif row.fill_ratio < 80:
            row.risk = "Warning"
        else:
            row.risk = "OK"

        # risk filter
        rf = filters.get("risk_filter")

        if rf == "HIGH" and row.risk != "Critical":
            continue
        if rf == "Medium" and row.risk != "Warning":
            continue
        if rf == "OK" and row.risk != "OK":
            continue

        final.append(row)

    return final


# ---------------- COLUMNS ----------------

def get_columns():

    return [
        {"label": _("Party Type"), "fieldname": "party_type", "width": 120},
        {"label": _("Customer / Supplier"), "fieldname": "party", "width": 260},

        {"label": _("Order Count"), "fieldname": "order_count", "fieldtype": "Int", "width": 120},

        {"label": _("Total Ordered"), "fieldname": "qty", "fieldtype": "Float"},
        {"label": _("Delivered"), "fieldname": "delivered_qty", "fieldtype": "Float"},
        {"label": _("Pending"), "fieldname": "pending_qty", "fieldtype": "Float"},

        {"label": _("Fill %"), "fieldname": "fill_ratio", "fieldtype": "Percent"},
        {"label": _("Risk Level"), "fieldname": "risk", "width": 120},
    ]
