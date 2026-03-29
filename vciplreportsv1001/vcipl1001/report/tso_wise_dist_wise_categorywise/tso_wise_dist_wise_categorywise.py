import frappe
from datetime import date

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

# ================= PERIOD =================
def apply_period_filters(filters):

    year = int(filters.get("year") or date.today().year)
    today = date.today()
    current_month = today.month

    # 🔥 AUTO QUARTER
    if filters.get("period_type") == "Quarter" and not filters.get("quarter"):

        if current_month in [4,5,6]:
            filters.quarter = "Q1"
        elif current_month in [7,8,9]:
            filters.quarter = "Q2"
        elif current_month in [10,11,12]:
            filters.quarter = "Q3"
        else:
            filters.quarter = "Q4"

    # 🔥 QUARTER
    if filters.get("period_type") == "Quarter":

        if filters.get("quarter") == "Q1":
            filters.from_date = f"{year}-04-01"
            filters.to_date = f"{year}-06-30"

        elif filters.get("quarter") == "Q2":
            filters.from_date = f"{year}-07-01"
            filters.to_date = f"{year}-09-30"

        elif filters.get("quarter") == "Q3":
            filters.from_date = f"{year}-10-01"
            filters.to_date = f"{year}-12-31"

        elif filters.get("quarter") == "Q4":
            filters.from_date = f"{year+1}-01-01"
            filters.to_date = f"{year+1}-03-31"

    # 🔥 HALF YEAR
    elif filters.get("period_type") == "Half Year":

        if filters.get("half_year") == "H1":
            filters.from_date = f"{year}-04-01"
            filters.to_date = f"{year}-09-30"

        elif filters.get("half_year") == "H2":
            filters.from_date = f"{year}-10-01"
            filters.to_date = f"{year+1}-03-31"

    # 🔥 YEAR (FINANCIAL)
    elif filters.get("period_type") == "Year":

        filters.from_date = f"{year}-04-01"
        filters.to_date = f"{year+1}-03-31"


# ================= EXECUTE =================
def execute(filters=None):
    filters = frappe._dict(filters or {})
    apply_period_filters(filters)
    return get_columns(filters), get_data(filters)


# ================= COLUMNS =================
def get_columns(filters):

    columns = [
        {"label": "Month", "fieldname": "month", "width": 90},
        {"label": "Head Sales Person", "fieldname": "parent_sales_person", "width": 180},
        {"label": "TSO", "fieldname": "tso", "width": 180},
        {"label": "Sales Region", "fieldname": "region", "width": 150},
        {"label": "Sales Territory", "fieldname": "territory", "width": 150},
        {"label": "Customer", "fieldname": "customer", "width": 220},
        {"label": "Customer Group", "fieldname": "customer_group", "width": 180},
        {"label": "Category", "fieldname": "category", "width": 160},
    ]

    if filters.get("include_customer_sub_group"):
        columns.append({
            "label": "Customer Sub Group",
            "fieldname": "customer_sub_group",
            "width": 160
        })

    columns += [
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 120},
        {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 140},
        {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 120},
    ]

    return columns


# ================= DATA =================
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

    if filters.get("customer_group"):
        conditions += " AND c.customer_group = %(customer_group)s"
        values["customer_group"] = filters.get("customer_group")

    if filters.get("tso"):
        conditions += " AND st.sales_person = %(tso)s"
        values["tso"] = filters.get("tso")

    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.get("parent_sales_person")

    if filters.get("region"):
        conditions += " AND sp.custom_region = %(region)s"
        values["region"] = filters.get("region")

    if filters.get("territory"):
        conditions += " AND sp.custom_territory = %(territory)s"
        values["territory"] = filters.get("territory")

    if filters.get("main_group"):
        conditions += " AND i.custom_main_group = %(main_group)s"
        values["main_group"] = filters.get("main_group")

    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            st.sales_person as tso,
            sp.parent_sales_person,
            sp.custom_region as region,
            sp.custom_territory as territory,
            si.customer_name as customer,
            c.customer_group,
            c.custom_sub_group as customer_sub_group,
            i.custom_main_group as category,
            si.customer as customer_id,
            SUM(sii.qty) as qty,
            SUM(sii.amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
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
            sp.custom_territory,
            si.customer,
            c.customer_group,
            c.custom_sub_group,
            i.custom_main_group
        ORDER BY MONTH(si.posting_date), st.sales_person
    """, values, as_dict=1)

    result = []

    total_qty = 0
    total_amount = 0
    total_target = 0

    for row in data:

        month = int(row.month)

        target = get_target(row.customer_id, row.tso, month)
        target = float(target or 0)

        achieved = (row.amount / target * 100) if target else 0

        total_qty += row.qty or 0
        total_amount += row.amount or 0
        total_target += target or 0

        record = {
            "month": MONTHS[month - 1],
            "parent_sales_person": row.parent_sales_person,
            "tso": row.tso,
            "region": row.region,
            "territory": row.territory,
            "customer": row.customer,
            "customer_group": row.customer_group,
            "category": row.category,
            "qty": row.qty,
            "amount": row.amount,
            "target": target,
            "achieved": achieved
        }

        if filters.get("include_customer_sub_group"):
            record["customer_sub_group"] = row.customer_sub_group

        result.append(record)

    overall = (total_amount / total_target * 100) if total_target else 0

    result.append({
        "month": "TOTAL",
        "qty": total_qty,
        "amount": total_amount,
        "target": total_target,
        "achieved": overall
    })

    return result


# ================= TARGET =================
def get_target(customer, sales_person, month):

    fieldname = MONTH_FIELD_MAP.get(month)

    if not fieldname:
        return 0

    return frappe.db.get_value(
        "Sales Team",
        {"parent": customer, "sales_person": sales_person},
        fieldname
    ) or 0