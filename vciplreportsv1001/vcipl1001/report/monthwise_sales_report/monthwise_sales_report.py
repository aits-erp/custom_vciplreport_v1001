import frappe


@frappe.whitelist()
def get_month_breakup(customer=None, customer_group=None, month=None):
    conditions = []
    values = {}

    if customer:
        conditions.append("si.customer = %(customer)s")
        values["customer"] = customer

    if customer_group:
        conditions.append("c.customer_group = %(customer_group)s")
        values["customer_group"] = customer_group

    if month:
        conditions.append("MONTHNAME(si.posting_date) = %(month)s")
        values["month"] = month

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = " AND " + condition_sql

    data = frappe.db.sql(f"""
        SELECT
            MONTHNAME(si.posting_date) AS month,
            SUM(sii.amount) AS total
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.docstatus = 1
        {condition_sql}
        GROUP BY MONTH(si.posting_date)
        ORDER BY MONTH(si.posting_date)
    """, values, as_dict=True)

    labels = [d.month for d in data]
    values = [d.total for d in data]

    html = frappe.render_template(
        "vciplreportsv1001/vcipl1001/report/monthwise_sales_report/monthwise_sales_report.html",
        {"data": data}
    )

    return {
        "labels": labels,
        "values": values,
        "html": html
    }
