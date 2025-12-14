import frappe

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# ---------------------- COLUMNS ----------------------
def get_columns():
    return [
        {"label": "Supplier Group", "fieldname": "supplier_group", "width": 160},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "HTML", "width": 240},

        {"label": "Jan", "fieldname": "jan", "fieldtype": "Currency", "width": 110},
        {"label": "Feb", "fieldname": "feb", "fieldtype": "Currency", "width": 110},
        {"label": "Mar", "fieldname": "mar", "fieldtype": "Currency", "width": 110},
        {"label": "Apr", "fieldname": "apr", "fieldtype": "Currency", "width": 110},
        {"label": "May", "fieldname": "may", "fieldtype": "Currency", "width": 110},
        {"label": "Jun", "fieldname": "jun", "fieldtype": "Currency", "width": 110},
        {"label": "Jul", "fieldname": "jul", "fieldtype": "Currency", "width": 110},
        {"label": "Aug", "fieldname": "aug", "fieldtype": "Currency", "width": 110},
        {"label": "Sep", "fieldname": "sep", "fieldtype": "Currency", "width": 110},
        {"label": "Oct", "fieldname": "oct", "fieldtype": "Currency", "width": 110},
        {"label": "Nov", "fieldname": "nov", "fieldtype": "Currency", "width": 110},
        {"label": "Dec", "fieldname": "dec", "fieldtype": "Currency", "width": 110},

        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 140}
    ]


# ---------------------- DATA ----------------------
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

    if filters.get("supplier_group"):
        sql += " AND pi.supplier_group = %s"
        values.append(filters["supplier_group"])

    if filters.get("month"):
        sql += " AND DATE_FORMAT(pi.posting_date, '%%b') = %s"
        values.append(filters["month"])

    sql += " GROUP BY pi.supplier, MONTH(pi.posting_date)"
    sql += " ORDER BY pi.supplier"

    raw = frappe.db.sql(sql, values, as_dict=True)
    if not raw:
        return []

    month_map = {
        1: "jan", 2: "feb", 3: "mar", 4: "apr",
        5: "may", 6: "jun", 7: "jul", 8: "aug",
        9: "sep", 10: "oct", 11: "nov", 12: "dec"
    }

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

        key = month_map[row.month]
        data_map[supplier][key] += row.amount or 0
        data_map[supplier]["total"] += row.amount or 0

    return list(data_map.values())


# ---------------------- POPUP BREAKUP ----------------------
@frappe.whitelist()
def get_month_breakup(supplier, supplier_group=None, month=None):

    sql = """
        SELECT
            DATE_FORMAT(posting_date, '%%b') AS month,
            SUM(grand_total) AS amount
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND supplier = %s
    """

    values = [supplier]

    if supplier_group:
        sql += " AND supplier_group = %s"
        values.append(supplier_group)

    if month:
        sql += " AND DATE_FORMAT(posting_date, '%%b') = %s"
        values.append(month)

    sql += " GROUP BY DATE_FORMAT(posting_date, '%%b')"

    rows = frappe.db.sql(sql, values, as_dict=True)

    if not rows:
        return {"html": "<b>No data found</b>", "labels": [], "values": []}

    html = """
        <h4>Purchase Details</h4>
        <table class="table table-bordered">
            <tr><th>Month</th><th>Amount</th></tr>
    """

    labels, values_list = [], []

    for r in rows:
        html += f"<tr><td>{r.month}</td><td>{frappe.utils.fmt_money(r.amount)}</td></tr>"
        labels.append(r.month)
        values_list.append(float(r.amount))

    html += "</table>"

    return {
        "html": html,
        "labels": labels,
        "values": values_list
    }
