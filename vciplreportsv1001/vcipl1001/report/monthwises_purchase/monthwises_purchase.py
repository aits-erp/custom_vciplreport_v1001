import frappe

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

# ---------------------- COLUMNS ----------------------
def get_columns():
    return [
        {"label": "Supplier Group", "fieldname": "supplier_group", "fieldtype": "Data", "width": 150},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "HTML", "width": 220},

        {"label": "Jan", "fieldname": "jan", "fieldtype": "Currency", "width": 120},
        {"label": "Feb", "fieldname": "feb", "fieldtype": "Currency", "width": 120},
        {"label": "Mar", "fieldname": "mar", "fieldtype": "Currency", "width": 120},
        {"label": "Apr", "fieldname": "apr", "fieldtype": "Currency", "width": 120},
        {"label": "May", "fieldname": "may", "fieldtype": "Currency", "width": 120},
        {"label": "Jun", "fieldname": "jun", "fieldtype": "Currency", "width": 120},
        {"label": "Jul", "fieldname": "jul", "fieldtype": "Currency", "width": 120},
        {"label": "Aug", "fieldname": "aug", "fieldtype": "Currency", "width": 120},
        {"label": "Sep", "fieldname": "sep", "fieldtype": "Currency", "width": 120},
        {"label": "Oct", "fieldname": "oct", "fieldtype": "Currency", "width": 120},
        {"label": "Nov", "fieldname": "nov", "fieldtype": "Currency", "width": 120},
        {"label": "Dec", "fieldname": "dec", "fieldtype": "Currency", "width": 120},

        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 150}
    ]


# ---------------------- MAIN DATA ----------------------
def get_data(filters):
    sql = """
        SELECT
            pi.supplier_group,
            pi.supplier,
            MONTH(pi.posting_date) AS month,
            SUM(pi.grand_total) AS amount
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1
    """
    values = []

    if filters.get("company"):
        sql += " AND pi.company = %s"
        values.append(filters["company"])

    if filters.get("year"):
        sql += " AND YEAR(pi.posting_date) = %s"
        values.append(filters["year"])

    sql += " GROUP BY pi.supplier, MONTH(pi.posting_date)"
    sql += " ORDER BY pi.supplier"

    raw = frappe.db.sql(sql, values, as_dict=True)

    if not raw:
        return []

    # ---------------- Pivot Transform ----------------
    data_map = {}

    for row in raw:
        supplier = row.supplier

        if supplier not in data_map:
            data_map[supplier] = {
                "supplier_group": row.supplier_group,
                "supplier": f'<a href="#" class="supplier-link" data-supplier="{supplier}">{supplier}</a>',
                "jan": 0, "feb": 0, "mar": 0, "apr": 0,
                "may": 0, "jun": 0, "jul": 0, "aug": 0,
                "sep": 0, "oct": 0, "nov": 0, "dec": 0,
                "total": 0
            }

        month_map = {
            1: "jan", 2: "feb", 3: "mar", 4: "apr",
            5: "may", 6: "jun", 7: "jul", 8: "aug",
            9: "sep", 10: "oct", 11: "nov", 12: "dec"
        }

        month_key = month_map[row.month]
        data_map[supplier][month_key] = row.amount or 0
        data_map[supplier]["total"] += row.amount or 0

    return list(data_map.values())


# ---------------------- BAR-CHART POPUP ----------------------
@frappe.whitelist()
def get_month_breakup(supplier, company=None, year=None):

    sql = """
        SELECT 
            MONTH(posting_date) AS month_num,
            DATE_FORMAT(posting_date, '%%b') AS month,
            SUM(grand_total) AS amount
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND supplier = %s
    """

    values = [supplier]

    if company:
        sql += " AND company = %s"
        values.append(company)

    if year:
        sql += " AND YEAR(posting_date) = %s"
        values.append(year)

    sql += " GROUP BY MONTH(posting_date) ORDER BY MONTH(posting_date)"

    rows = frappe.db.sql(sql, values, as_dict=True)

    if not rows:
        return {
            "html": "<b>No data found.</b>",
            "labels": [],
            "values": []
        }

    # ------- HTML TABLE -------
    html = """
        <h4>Month-wise Purchases</h4>
        <table class="table table-bordered">
            <tr><th>Month</th><th>Amount</th></tr>
    """

    labels = []
    values = []

    for r in rows:
        html += f"<tr><td>{r.month}</td><td>{frappe.utils.fmt_money(r.amount)}</td></tr>"
        labels.append(r.month)
        values.append(float(r.amount))

    html += "</table>"

    return {
        "html": html,
        "labels": labels,
        "values": values
    }
