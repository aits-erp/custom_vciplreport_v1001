import frappe

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

# ✅ Your month fields (Data type)
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


def execute(filters=None):
    filters = frappe._dict(filters or {})
    return get_columns(), get_data(filters)


# ✅ COLUMNS
def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "width": 90},
        {"label": "TSO (Territory)", "fieldname": "tso", "width": 150},
        {"label": "Sales Person", "fieldname": "sales_person", "width": 180},
        {"label": "Customer", "fieldname": "customer", "width": 200},
        {"label": "Category", "fieldname": "category", "width": 150},
        {"label": "Main Group", "fieldname": "main_group", "width": 150},
        {"label": "Item", "fieldname": "item", "width": 180},
        {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 120},
    ]


def get_data(filters):

    conditions = ""
    values = {}

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
        values["company"] = filters.get("company")

    # ✅ CHECK IF custom_territory EXISTS
    sales_person_fields = [f.fieldname for f in frappe.get_meta("Sales Person").fields]

    if "custom_territory" in sales_person_fields:
        tso_field = "sp.custom_territory"
    else:
        tso_field = "st.sales_person"

    # ✅ MAIN QUERY
    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            {tso_field} as tso,
            st.sales_person as sales_person,
            si.customer as customer_id,
            si.customer_name as customer,
            sii.item_group as category,
            i.custom_main_group as main_group,
            sii.item_name as item,
            SUM(sii.amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabItem` i ON i.name = sii.item_code
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY
            MONTH(si.posting_date),
            tso,
            st.sales_person,
            si.customer,
            sii.item_group,
            i.custom_main_group,
            sii.item_name
        ORDER BY MONTH(si.posting_date)
    """, values, as_dict=1)

    result = []

    for row in data:

        month = int(row.month) if row.month else None

        target = get_target(row.customer_id, row.sales_person, month)

        # ✅ 🔥 FIX: Convert string → float safely
        try:
            target = float(target)
        except:
            target = 0

        achieved = (row.amount / target * 100) if target else 0

        result.append({
            "month": MONTHS[month - 1] if month else "",
            "tso": row.tso or "",
            "sales_person": row.sales_person or "",
            "customer": row.customer or "",
            "category": row.category or "",
            "main_group": row.main_group or "",
            "item": row.item or "",
            "amount": row.amount or 0,
            "target": target,
            "achieved": achieved
        })

    return result


# ✅ TARGET FROM CUSTOMER → SALES TEAM
def get_target(customer, sales_person, month):

    if not customer or not sales_person or not month:
        return 0

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    target = frappe.db.get_value(
        "Sales Team",
        {
            "parent": customer,
            "sales_person": sales_person
        },
        fieldname
    )

    return target or 0