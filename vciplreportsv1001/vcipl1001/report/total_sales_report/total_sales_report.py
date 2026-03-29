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

    # AUTO QUARTER
    if filters.get("period_type") == "Quarter" and not filters.get("quarter"):

        if current_month in [4,5,6]:
            filters.quarter = "Q1"
        elif current_month in [7,8,9]:
            filters.quarter = "Q2"
        elif current_month in [10,11,12]:
            filters.quarter = "Q3"
        else:
            filters.quarter = "Q4"

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

    elif filters.get("period_type") == "Half Year":

        if filters.get("half_year") == "H1":
            filters.from_date = f"{year}-04-01"
            filters.to_date = f"{year}-09-30"

        elif filters.get("half_year") == "H2":
            filters.from_date = f"{year}-10-01"
            filters.to_date = f"{year+1}-03-31"

    elif filters.get("period_type") == "Year":

        filters.from_date = f"{year}-04-01"
        filters.to_date = f"{year+1}-03-31"


# ================= EXECUTE =================
def execute(filters=None):
    filters = frappe._dict(filters or {})
    apply_period_filters(filters)
    return get_columns(), get_data(filters)


# ================= COLUMNS =================
def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Head Sales Person", "fieldname": "parent_sales_person", "width": 200},
        {"label": "Sales Region", "fieldname": "region", "width": 150},
        {"label": "Customer", "fieldname": "customer", "width": 220},
        {"label": "TSO", "fieldname": "tso", "width": 180},
        {"label": "Sales Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved", "fieldtype": "Percent", "width": 130},
    ]


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

    if filters.get("tso"):
        conditions += " AND st.sales_person = %(tso)s"
        values["tso"] = filters.get("tso")

    if filters.get("parent_sales_person"):
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.get("parent_sales_person")

    if filters.get("region"):
        conditions += " AND sp.custom_region = %(region)s"
        values["region"] = filters.get("region")

    data = frappe.db.sql(f"""
        SELECT
            MONTH(si.posting_date) as month,
            si.customer_name as customer,
            st.sales_person as tso,
            sp.parent_sales_person,
            sp.custom_region as region,
            si.customer as customer_id,
            SUM(sii.amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN `tabSales Team` st ON st.parent = si.name AND st.idx = 1
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
        {conditions}
        GROUP BY 
            MONTH(si.posting_date),
            si.customer,
            st.sales_person,
            sp.parent_sales_person,
            sp.custom_region
        ORDER BY YEAR(si.posting_date), MONTH(si.posting_date)
    """, values, as_dict=1)

    result = []

    total_amount = 0
    total_target = 0

    for row in data:

        month = int(row.month)

        target = get_target(row.customer_id, row.tso, month)
        target = float(target or 0)

        achieved = (row.amount / target * 100) if target else 0

        total_amount += row.amount or 0
        total_target += target or 0

        result.append({
            "month": MONTHS[month - 1],
            "parent_sales_person": row.parent_sales_person,
            "region": row.region,
            "customer": row.customer,
            "tso": row.tso,
            "amount": row.amount,
            "target": target,
            "achieved": achieved
        })

    overall = (total_amount / total_target * 100) if total_target else 0

    result.append({
        "month": "TOTAL",
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