import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    mode = filters.get("mode", "Customer")
    level = filters.get("level")

    # ---------------- CUSTOMER MODE ----------------
    if mode == "Customer":
        if not level:
            return columns("Customer Group"), customer_group(filters)
        if level == "sub_group":
            return columns("Sub Group"), customer_sub_group(filters)
        if level == "customer":
            return columns("Customer"), customer(filters)
        if level == "invoice":
            return columns("Invoice"), customer_invoice(filters)

    # ---------------- ITEM MODE ----------------
    if mode == "Item":
        if not level:
            return columns("Item Group"), item_group(filters)
        if level == "main":
            return columns("Main Group"), item_main(filters)
        if level == "sub":
            return columns("Sub Group"), item_sub(filters)
        if level == "sub1":
            return columns("Sub Group 1"), item_sub1(filters)
        if level == "item":
            return columns("Item"), item(filters)
        if level == "invoice":
            return columns("Invoice"), item_invoice(filters)

    return [], []


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------

def columns(label):
    cols = [
        {"label": label, "fieldname": "label", "width": 350},
        {"label": "Value", "fieldname": "value", "fieldtype": "Currency", "width": 160},
        {"fieldname": "drill", "hidden": 1},
    ]

    if label == "Invoice":
        cols.insert(1, {"label": "Posting Date", "fieldname": "posting_date", "width": 120})

    return cols


# --------------------------------------------------
# CUSTOMER FLOW
# --------------------------------------------------

def customer_group(filters):
    rows = frappe.db.sql("""
        SELECT customer_group, SUM(base_net_total) value
        FROM `tabSales Invoice`
        WHERE docstatus=1
        GROUP BY customer_group
    """, as_dict=True)

    return [{
        "label": r.customer_group,
        "value": flt(r.value),
        "drill": frappe.as_json({"level": "sub_group", "customer_group": r.customer_group})
    } for r in rows]


def customer_sub_group(filters):
    if not frappe.db.has_column("Customer", "custom_sub_group"):
        return []

    rows = frappe.db.sql("""
        SELECT c.custom_sub_group, SUM(si.base_net_total) value
        FROM `tabSales Invoice` si
        JOIN `tabCustomer` c ON c.name=si.customer
        WHERE si.docstatus=1 AND c.customer_group=%(customer_group)s
        GROUP BY c.custom_sub_group
    """, filters, as_dict=True)

    return [{
        "label": r.custom_sub_group,
        "value": flt(r.value),
        "drill": frappe.as_json({
            "level": "customer",
            "customer_group": filters.customer_group,
            "custom_sub_group": r.custom_sub_group
        })
    } for r in rows]


def customer(filters):
    rows = frappe.db.sql("""
        SELECT c.name, c.customer_name, SUM(si.base_net_total) value
        FROM `tabSales Invoice` si
        JOIN `tabCustomer` c ON c.name=si.customer
        WHERE si.docstatus=1
          AND c.customer_group=%(customer_group)s
          AND c.custom_sub_group=%(custom_sub_group)s
        GROUP BY c.name
    """, filters, as_dict=True)

    return [{
        "label": r.customer_name,
        "value": flt(r.value),
        "drill": frappe.as_json({
            "level": "invoice",
            "customer": r.name
        })
    } for r in rows]


def customer_invoice(filters):
    return frappe.db.sql("""
        SELECT
            si.name label,
            si.posting_date,
            si.base_net_total value
        FROM `tabSales Invoice` si
        WHERE si.customer=%(customer)s AND si.docstatus=1
    """, filters, as_dict=True)


# --------------------------------------------------
# ITEM FLOW
# --------------------------------------------------

def item_group(filters):
    rows = frappe.db.sql("""
        SELECT i.item_group, SUM(sii.base_net_amount) value
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name=sii.parent
        JOIN `tabItem` i ON i.name=sii.item_code
        WHERE si.docstatus=1
        GROUP BY i.item_group
    """, as_dict=True)

    return [{
        "label": r.item_group,
        "value": flt(r.value),
        "drill": frappe.as_json({"level": "main", "item_group": r.item_group})
    } for r in rows]


def item_main(filters):
    if not frappe.db.has_column("Item", "custom_main_group"):
        return []

    rows = frappe.db.sql("""
        SELECT i.custom_main_group, SUM(sii.base_net_amount) value
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name=sii.parent
        JOIN `tabItem` i ON i.name=sii.item_code
        WHERE i.item_group=%(item_group)s
        GROUP BY i.custom_main_group
    """, filters, as_dict=True)

    return [{
        "label": r.custom_main_group,
        "value": flt(r.value),
        "drill": frappe.as_json({
            "level": "sub",
            "item_group": filters.item_group,
            "custom_main_group": r.custom_main_group
        })
    } for r in rows]


def item_sub(filters):
    if not frappe.db.has_column("Item", "custom_sub_group"):
        return []

    rows = frappe.db.sql("""
        SELECT i.custom_sub_group, SUM(sii.base_net_amount) value
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name=sii.parent
        JOIN `tabItem` i ON i.name=sii.item_code
        WHERE i.custom_main_group=%(custom_main_group)s
        GROUP BY i.custom_sub_group
    """, filters, as_dict=True)

    return [{
        "label": r.custom_sub_group,
        "value": flt(r.value),
        "drill": frappe.as_json({
            "level": "sub1",
            "custom_sub_group": r.custom_sub_group
        })
    } for r in rows]


def item_sub1(filters):
    if not frappe.db.has_column("Item", "custom_sub_group1"):
        return []

    rows = frappe.db.sql("""
        SELECT i.custom_sub_group1, SUM(sii.base_net_amount) value
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name=sii.parent
        JOIN `tabItem` i ON i.name=sii.item_code
        WHERE i.custom_sub_group=%(custom_sub_group)s
        GROUP BY i.custom_sub_group1
    """, filters, as_dict=True)

    return [{
        "label": r.custom_sub_group1,
        "value": flt(r.value),
        "drill": frappe.as_json({
            "level": "item",
            "custom_sub_group1": r.custom_sub_group1
        })
    } for r in rows]


def item(filters):
    rows = frappe.db.sql("""
        SELECT i.name, i.item_name, SUM(sii.base_net_amount) value
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name=sii.parent
        JOIN `tabItem` i ON i.name=sii.item_code
        WHERE i.custom_sub_group1=%(custom_sub_group1)s
        GROUP BY i.name
    """, filters, as_dict=True)

    return [{
        "label": r.item_name,
        "value": flt(r.value),
        "drill": frappe.as_json({
            "level": "invoice",
            "item_code": r.name
        })
    } for r in rows]


def item_invoice(filters):
    return frappe.db.sql("""
        SELECT
            si.name label,
            si.posting_date,
            sii.base_net_amount value
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent=si.name
        WHERE sii.item_code=%(item_code)s AND si.docstatus=1
    """, filters, as_dict=True)
