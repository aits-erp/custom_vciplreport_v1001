import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}

    if filters.get("from_date") and filters.get("to_date"):
        if filters.from_date > filters.to_date:
            frappe.throw(_("To Date must be greater than or equal to From Date"))

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": _("Subcontract Order"),
            "fieldtype": "Dynamic Link",
            "fieldname": "subcontract_order",
            "options": "order_type",
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
            "width": 220,
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

        if transferred_qty < flt(row.get("reqd_qty")):
            row["p_qty"] = flt(row.get("reqd_qty")) - transferred_qty
            data.append(row)

    return data


def get_order_items_to_supply(filters):
    supplied_items_table = (
        "Purchase Order Item Supplied"
        if filters.order_type == "Purchase Order"
        else "Subcontracting Order Supplied Item"
    )

    parent_table = f"`tab{filters.order_type}`"
    child_table = f"`tab{supplied_items_table}`"

    conditions = """
        parent.per_received < 100
        AND parent.docstatus = 1
        AND parent.transaction_date BETWEEN %(from_date)s AND %(to_date)s
    """

    if filters.get("supplier"):
        conditions += " AND parent.supplier = %(supplier)s"

    if filters.order_type == "Purchase Order":
        conditions += " AND parent.is_old_subcontracting_flow = 1"

    if filters.get("item_code"):
        conditions += " AND child.rm_item_code = %(item_code)s"

    query = f"""
        SELECT
            parent.name AS subcontract_order,
            %(order_type)s AS order_type,
            parent.transaction_date AS date,
            parent.supplier_name AS supplier_name,
            child.rm_item_code,
            child.item_name,
            child.rate,
            child.required_qty AS reqd_qty,
            child.supplied_qty AS transferred_qty
        FROM {parent_table} parent
        INNER JOIN {child_table} child
            ON child.parent = parent.name
        WHERE {conditions}
        ORDER BY parent.transaction_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)