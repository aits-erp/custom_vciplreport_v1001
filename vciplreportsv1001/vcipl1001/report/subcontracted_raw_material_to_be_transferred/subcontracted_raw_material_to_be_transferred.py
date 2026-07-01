import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}

    if filters.get("from_date") and filters.get("to_date"):
        if filters.from_date > filters.to_date:
            frappe.throw(_("To Date must be greater than or equal to From Date"))

    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


def get_columns(filters):
    return [
        {
            "label": _("Subcontract Order"),
            "fieldtype": "Link",
            "fieldname": "subcontract_order",
            "options": filters.order_type,
            "width": 180,
        },
        {
            "label": _("Date"),
            "fieldtype": "Date",
            "fieldname": "date",
            "width": 110,
        },
        {
            "label": _("Supplier Name"),
            "fieldtype": "Data",
            "fieldname": "supplier_name",
            "width": 220,
        },
        {
            "label": _("Item Name"),
            "fieldtype": "Data",
            "fieldname": "item_name",
            "width": 250,
        },
        {
            "label": _("Rate"),
            "fieldtype": "Currency",
            "fieldname": "rate",
            "width": 120,
        },
        {
            "label": _("Required Quantity"),
            "fieldtype": "Float",
            "fieldname": "reqd_qty",
            "width": 150,
        },
        {
            "label": _("Transferred Quantity"),
            "fieldtype": "Float",
            "fieldname": "transferred_qty",
            "width": 170,
        },
        {
            "label": _("Pending Quantity"),
            "fieldtype": "Float",
            "fieldname": "p_qty",
            "width": 150,
        },
    ]


def get_data(filters):
    order_rm_item_details = get_order_items_to_supply(filters)

    data = []

    for row in order_rm_item_details:
        transferred_qty = flt(row.get("transferred_qty"))
        required_qty = flt(row.get("reqd_qty"))

        if transferred_qty < required_qty:
            row["p_qty"] = required_qty - transferred_qty
            data.append(row)

    return data


def get_order_items_to_supply(filters):

    if filters.order_type == "Purchase Order":
        supplied_items_table = "Purchase Order Item Supplied"
    else:
        supplied_items_table = "Subcontracting Order Supplied Item"

    parent_table = f"`tab{filters.order_type}`"
    child_table = f"`tab{supplied_items_table}`"

    conditions = [
        "parent.per_received < 100",
        "parent.docstatus = 1",
        "parent.transaction_date >= %(from_date)s",
        "parent.transaction_date <= %(to_date)s",
    ]

    if filters.get("supplier"):
        conditions.append("parent.supplier = %(supplier)s")

    if filters.get("item_code"):
        conditions.append("child.rm_item_code = %(item_code)s")

    if filters.order_type == "Purchase Order":
        conditions.append("parent.is_old_subcontracting_flow = 1")

    conditions = " AND ".join(conditions)

    query = f"""
        SELECT
            parent.name AS subcontract_order,
            parent.transaction_date AS date,
            parent.supplier_name AS supplier_name,
            child.rm_item_code,
            item.item_name AS item_name,
            child.rate,
            child.required_qty AS reqd_qty,
            child.supplied_qty AS transferred_qty
        FROM {parent_table} parent
        INNER JOIN {child_table} child
            ON child.parent = parent.name
        LEFT JOIN `tabItem` item
            ON item.name = child.rm_item_code
        WHERE {conditions}
        ORDER BY parent.transaction_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)