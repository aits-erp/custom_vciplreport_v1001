import frappe


@frappe.whitelist()
def get_month_breakup(supplier=None, supplier_group=None, month=None):
    conditions = []
    values = {}

    if supplier:
        conditions.append("pi.supplier = %(supplier)s")
        values["supplier"] = supplier

    if supplier_group:
        conditions.append("s.supplier_group = %(supplier_group)s")
        values["supplier_group"] = supplier_group

    if month:
        conditions.append("MONTHNAME(pi.posting_date) = %(month)s")
        values["month"] = month

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = " AND " + condition_sql

    data = frappe.db.sql(f"""
        SELECT
            MONTHNAME(pi.posting_date) AS month,
            SUM(pii.amount) AS total
        FROM `tabPurchase Invoice` pi
        INNER JOIN `tabPurchase Invoice Item` pii ON pii.parent = pi.name
        INNER JOIN `tabSupplier` s ON s.name = pi.supplier
        WHERE pi.docstatus = 1
        {condition_sql}
        GROUP BY MONTH(pi.posting_date)
        ORDER BY MONTH(pi.posting_date)
    """, values, as_dict=True)

    labels = [d.month for d in data]
    values = [d.total for d in data]

    html = frappe.render_template(
        "vciplreportsv1001/vcipl1001/report/monthwises_purchase/monthwises_purchase.html",
        {"data": data}
    )

    return {
        "labels": labels,
        "values": values,
        "html": html
    }
