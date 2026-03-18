import frappe

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

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
    return get_columns(filters), get_data(filters)


# ✅ COLUMNS
def get_columns(filters):

    columns = [
        {"label": "Month", "fieldname": "month", "width": 90},
        {"label": "TSO", "fieldname": "tso", "width": 150},
        {"label": "Parent Sales Person", "fieldname": "parent_sales_person", "width": 180},
        {"label": "Sales Person", "fieldname": "sales_person", "width": 180},
        {"label": "Customer", "fieldname": "customer", "width": 200},
    ]

    if filters.get("show_category"):
        columns.append({"label": "Category", "fieldname": "category", "width": 150})

    if filters.get("show_item"):
        columns.append({"label": "Item", "fieldname": "item", "width": 180})

    columns += [
        {"label": "Main Group", "fieldname": "main_group", "width": 150},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 120},
        {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 120},
    ]

    return columns


def get_data(filters):

    conditions = ""
    values = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
        values["company"] = filters.get("company")

    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.get("customer")

    if filters.get("item_group"):
        conditions += " AND sii.item_group = %(item_group)s"
        values["item_group"] = filters.get("item_group")

    if filters.get("item"):
        conditions += " AND sii.item_code = %(item)s"
        values["item"] = filters.get("item")

    if filters.get("warehouse"):
        conditions += " AND sii.warehouse = %(warehouse)s"
        values["warehouse"] = filters.get("warehouse")

    if filters.get("tso"):
        conditions += " AND st.sales_person = %(tso)s"
        values["tso"] = filters.get("tso")

    # ✅ dynamic fields
    sp_fields = [f.fieldname for f in frappe.get_meta("Sales Person").fields]
    item_fields = [f.fieldname for f in frappe.get_meta("Item").fields]

    tso_field = "sp.custom_territory" if "custom_territory" in sp_fields else "st.sales_person"
    parent_sp_field = "sp.parent_sales_person" if "parent_sales_person" in sp_fields else "''"
    main_group_field = "i.custom_main_group" if "custom_main_group" in item_fields else "''"

    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.get("parent_sales_person")

    # ✅ grouping logic
    group_by = ["MONTH(si.posting_date)", "st.sales_person"]

    if filters.get("show_item"):
        group_by.append("sii.item_code")
    elif filters.get("show_category"):
        group_by.append("sii.item_group")
    else:
        group_by.append("si.customer")

    group_by = ", ".join(group_by)

    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            {tso_field} as tso,
            {parent_sp_field} as parent_sales_person,
            st.sales_person as sales_person,
            si.customer as customer,
            sii.item_group as category,
            {main_group_field} as main_group,
            sii.item_name as item,
            SUM(sii.qty) as qty,
            SUM(sii.amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabItem` i ON i.name = sii.item_code
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY {group_by}
        ORDER BY MONTH(si.posting_date)
    """, values, as_dict=1)

    result = []

    total_qty = 0
    total_amount = 0
    total_target = 0

    for row in data:

        month = int(row.month)

        target = get_target(row.customer, row.sales_person, month)

        try:
            target = float(target)
        except:
            target = 0

        achieved = (row.amount / target * 100) if target else 0

        total_qty += row.qty or 0
        total_amount += row.amount or 0
        total_target += target or 0

        d = {
            "month": MONTHS[month - 1],
            "tso": row.tso,
            "parent_sales_person": row.parent_sales_person,
            "sales_person": row.sales_person,
            "customer": row.customer,
            "main_group": row.main_group,
            "qty": row.qty,
            "amount": row.amount,
            "target": target,
            "achieved": achieved
        }

        if filters.get("show_category"):
            d["category"] = row.category

        if filters.get("show_item"):
            d["item"] = row.item

        result.append(d)

    overall = (total_amount / total_target * 100) if total_target else 0

    result.append({
        "month": "TOTAL",
        "qty": total_qty,
        "amount": total_amount,
        "target": total_target,
        "achieved": overall
    })

    return result


def get_target(customer, sales_person, month):

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    return frappe.db.get_value(
        "Sales Team",
        {"parent": customer, "sales_person": sales_person},
        fieldname
    ) or 0