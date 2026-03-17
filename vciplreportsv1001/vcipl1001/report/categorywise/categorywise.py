import frappe

# ✅ Month Names
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

# ✅ Month → Target Field Mapping
MONTH_FIELD_MAP = {
    1: "custom_january",
    2: "custom_february",
    3: "custom_march",
    4: "custom_april",
    5: "custom_may_",
    6: "custom_june",
    7: "custom_july",
    8: "custom_august",
    9: "custom_september",
    10: "custom_october",
    11: "custom_november",
    12: "custom_december"
}


# ✅ MAIN EXECUTE
def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


# ✅ COLUMNS
def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "width": 90},
        {"label": "TSO (Territory)", "fieldname": "tso", "width": 150},
        {"label": "Customer", "fieldname": "customer", "width": 200},
        {"label": "Category", "fieldname": "category", "width": 150},
        {"label": "Main Group", "fieldname": "main_group", "width": 150},
        {"label": "Item", "fieldname": "item", "width": 180},
        {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 120},
    ]


# ✅ MAIN DATA FUNCTION
def get_data(filters):

    conditions = ""
    values = {}

    # ✅ Date Filter
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    # ✅ Company Filter
    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
        values["company"] = filters.get("company")

    # ✅ Territory Filter
    if filters.get("tso"):
        conditions += " AND sp.custom_territory = %(tso)s"
        values["tso"] = filters.get("tso")

    # ✅ Customer Filter
    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.get("customer")

    # ✅ Category Filter
    if filters.get("item_group"):
        conditions += " AND sii.item_group = %(item_group)s"
        values["item_group"] = filters.get("item_group")

    # ✅ Main Group Filter
    if filters.get("main_group"):
        conditions += " AND sii.custome_main_group = %(main_group)s"
        values["main_group"] = filters.get("main_group")

    # ✅ Item Filter
    if filters.get("item"):
        conditions += " AND sii.item_code = %(item)s"
        values["item"] = filters.get("item")

    # ✅ Warehouse Filter
    if filters.get("warehouse"):
        conditions += " AND sii.warehouse = %(warehouse)s"
        values["warehouse"] = filters.get("warehouse")

    # 🔥 MAIN QUERY (FIXED + JOIN SALES PERSON)
    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            sp.custom_territory as tso,
            si.customer_name as customer,
            sii.item_group as category,
            sii.custome_main_group as main_group,
            sii.item_name as item,
            SUM(sii.amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY
            MONTH(si.posting_date),
            sp.custom_territory,
            si.customer_name,
            sii.item_group,
            sii.custome_main_group,
            sii.item_name
        ORDER BY MONTH(si.posting_date), tso
    """, values, as_dict=1)

    result = []

    for row in data:

        month = int(row.month) if row.month else None

        target = get_target(row.tso, row.category, month)

        achieved = (row.amount / target * 100) if target else 0

        result.append({
            "month": MONTHS[month - 1] if month else "",
            "tso": row.tso or "No Territory",
            "customer": row.customer or "",
            "category": row.category or "",
            "main_group": row.main_group or "",
            "item": row.item or "",
            "amount": row.amount or 0,
            "target": target,
            "achieved": achieved
        })

    return result


# ✅ TARGET FUNCTION
def get_target(tso, category, month):

    if not tso or not month:
        return 0

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    target = frappe.db.get_value(
        "TSO Target",   # 👈 your doctype
        {
            "territory": tso,   # 👈 IMPORTANT: match your doctype field
            "item_group": category
        },
        fieldname
    )

    return target or 0