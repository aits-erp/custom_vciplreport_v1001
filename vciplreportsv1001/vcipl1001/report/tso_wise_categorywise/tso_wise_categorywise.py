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


def get_categories(filters):

    if filters.get("custom_main_group"):
        return filters.get("custom_main_group")

    return frappe.db.sql_list("""
        SELECT DISTINCT custom_main_group
        FROM `tabItem`
        WHERE custom_main_group IS NOT NULL
        AND custom_main_group != ''
    """)


def get_columns(categories):

    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Region", "fieldname": "custom_region", "width": 150},
        {"label": "Head Sales Code", "fieldname": "custom_head_sales_code", "width": 150},
        {"label": "Head Sales Person", "fieldname": "parent_sales_person", "width": 200},
        {"label": "TSO", "fieldname": "tso", "width": 180},
        {"label": "Customer", "fieldname": "customer", "width": 220},
        {"label": "Customer Group", "fieldname": "customer_group", "width": 200},
    ]

    for cat in categories:
        safe = cat.replace(" ", "_").replace(".", "").replace("-", "_")

        columns.append({"label": f"{cat} Target", "fieldname": f"{safe}_target", "fieldtype": "Currency"})
        columns.append({"label": f"{cat} Achieved", "fieldname": f"{safe}_achieved", "fieldtype": "Currency"})
        columns.append({"label": f"{cat} %", "fieldname": f"{safe}_percent", "fieldtype": "Percent"})

    return columns


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

    # ✅ SINGLE HEAD SALES PERSON FILTER
    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.get("parent_sales_person")

    if filters.get("custom_region"):
        conditions += " AND sp.custom_region IN %(custom_region)s"
        values["custom_region"] = tuple(filters.get("custom_region"))

    if filters.get("custom_head_sales_code"):
        conditions += " AND sp.custom_head_sales_code IN %(custom_head_sales_code)s"
        values["custom_head_sales_code"] = tuple(filters.get("custom_head_sales_code"))

    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.get("customer")

    if filters.get("customer_group"):
        conditions += " AND c.customer_group = %(customer_group)s"
        values["customer_group"] = filters.get("customer_group")

    if filters.get("custom_main_group"):
        conditions += " AND i.custom_main_group IN %(custom_main_group)s"
        values["custom_main_group"] = tuple(filters.get("custom_main_group"))

    conditions += " AND i.custom_item_type = 'Finished Goods'"

    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            st.sales_person as tso,
            sp.parent_sales_person,
            sp.custom_region,
            sp.custom_head_sales_code,
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
            sp.custom_region,
            sp.custom_head_sales_code,
            si.customer,
            c.customer_group,
            i.custom_main_group
    """, values, as_dict=1)

    return data