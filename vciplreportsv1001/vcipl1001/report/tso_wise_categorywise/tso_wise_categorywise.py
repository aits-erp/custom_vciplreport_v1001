import frappe
from frappe.utils import flt

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

    categories = get_categories(filters)
    columns = get_columns(categories)
    data = get_data(filters, categories)

    return columns, data


# 🔹 GET CATEGORIES
def get_categories(filters):

    if filters.get("custom_main_group") and len(filters.get("custom_main_group")) > 0:
        return filters.get("custom_main_group")

    return frappe.db.sql_list("""
        SELECT DISTINCT custom_main_group
        FROM `tabItem`
        WHERE custom_main_group IS NOT NULL
        AND custom_main_group != ''
    """)


# 🔹 COLUMNS
def get_columns(categories):

    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Head Sales Person", "fieldname": "parent_sales_person", "width": 200},
        {"label": "TSO", "fieldname": "tso", "width": 180},
        {"label": "Customer", "fieldname": "customer", "width": 220},
        {"label": "Customer Group", "fieldname": "customer_group", "width": 200},
    ]

    for cat in categories:
        safe = cat.replace(" ", "_").replace(".", "").replace("-", "_")

        columns.append({
            "label": f"{cat} Target",
            "fieldname": f"{safe}_target",
            "fieldtype": "Currency"
        })
        columns.append({
            "label": f"{cat} Achieved",
            "fieldname": f"{safe}_achieved",
            "fieldtype": "Currency"
        })
        columns.append({
            "label": f"{cat} %",
            "fieldname": f"{safe}_percent",
            "fieldtype": "Percent"
        })

    return columns


# 🔹 DATA
def get_data(filters, categories):

    conditions = ""
    values = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    if filters.get("sales_person"):
        conditions += " AND st.sales_person = %(sales_person)s"
        values["sales_person"] = filters.get("sales_person")

    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.get("customer")

    if filters.get("customer_group"):
        conditions += " AND c.customer_group = %(customer_group)s"
        values["customer_group"] = filters.get("customer_group")

    # 🔥 CATEGORY FILTER
    if filters.get("custom_main_group") and len(filters.get("custom_main_group")) > 0:
        conditions += " AND i.custom_main_group IN %(custom_main_group)s"
        values["custom_main_group"] = tuple(filters.get("custom_main_group"))

    # 🔥 ALWAYS FINISHED GOODS
    conditions += " AND i.custom_item_type = 'Finished Goods'"

    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            st.sales_person as tso,
            sp.parent_sales_person,
            si.customer_name as customer,
            c.customer_group,
            si.customer as customer_id,
            i.custom_main_group as category,
            SUM(sii.base_net_amount) as achieved
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabItem` i ON i.name = sii.item_code
        LEFT JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY 
            MONTH(si.posting_date),
            st.sales_person,
            sp.parent_sales_person,
            si.customer,
            c.customer_group,
            i.custom_main_group
    """, values, as_dict=1)

    result = {}
    totals = {}

    for row in data:
        key = (row.month, row.tso, row.customer)

        if key not in result:
            result[key] = {
                "month": MONTHS[int(row.month) - 1],
                "parent_sales_person": row.parent_sales_person,
                "tso": row.tso,
                "customer": row.customer,
                "customer_group": row.customer_group
            }

            for cat in categories:
                safe = cat.replace(" ", "_").replace(".", "").replace("-", "_")

                result[key][f"{safe}_target"] = 0
                result[key][f"{safe}_achieved"] = 0
                result[key][f"{safe}_percent"] = 0

                totals.setdefault(cat, {"target": 0, "achieved": 0})

        cat = row.category

        if cat in categories:
            safe = cat.replace(" ", "_").replace(".", "").replace("-", "_")

            target = flt(get_target(row.customer_id, row.tso, int(row.month)))
            achieved = flt(row.achieved)
            percent = (achieved / target * 100) if target else 0

            result[key][f"{safe}_target"] += target
            result[key][f"{safe}_achieved"] += achieved
            result[key][f"{safe}_percent"] = percent

            totals[cat]["target"] += target
            totals[cat]["achieved"] += achieved

    # 🔥 TOTAL ROW
    total_row = {"month": "TOTAL"}

    for cat in categories:
        safe = cat.replace(" ", "_").replace(".", "").replace("-", "_")

        t = totals[cat]["target"]
        a = totals[cat]["achieved"]
        p = (a / t * 100) if t else 0

        total_row[f"{safe}_target"] = t
        total_row[f"{safe}_achieved"] = a
        total_row[f"{safe}_percent"] = p

    return list(result.values()) + [total_row]


# 🔹 TARGET
def get_target(customer, sales_person, month):

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    return frappe.db.get_value(
        "Sales Team",
        {"parent": customer, "sales_person": sales_person},
        fieldname
    ) or 0