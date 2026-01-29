import frappe

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {
            "label": "Pricing Rule",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Pricing Rule",
            "width": 130
        },
        {
            "label": "Title",
            "fieldname": "title",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "Apply On",
            "fieldname": "apply_on",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Customer",
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 240
        },
        {
            "label": "Item / Brand",
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Enabled",
            "fieldname": "enabled",
            "fieldtype": "Check",
            "width": 80
        }
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters.get("customer"):
        conditions.append("pr.customer = %(customer)s")
        params["customer"] = filters["customer"]

    if filters.get("apply_on"):
        conditions.append("pr.apply_on = %(apply_on)s")
        params["apply_on"] = filters["apply_on"]

    if filters.get("enabled") is not None:
        conditions.append("pr.enabled = %(enabled)s")
        params["enabled"] = filters["enabled"]

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            pr.name,
            pr.title,
            pr.apply_on,
            cust.customer_name,
            COALESCE(prd.item_code, prd.brand) AS item_code,
            pr.enabled
        FROM `tabPricing Rule` pr
        LEFT JOIN `tabCustomer` cust
            ON cust.name = pr.customer
        LEFT JOIN `tabPricing Rule Detail` prd
            ON prd.parent = pr.name
            AND prd.parenttype = 'Pricing Rule'
            AND prd.parentfield = 'items'
        {where_clause}
        ORDER BY pr.modified DESC
    """

    return frappe.db.sql(query, params, as_dict=True)
