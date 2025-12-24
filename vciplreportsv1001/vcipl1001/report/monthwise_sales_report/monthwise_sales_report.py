import frappe

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}


def execute(filters=None):
    filters = filters or {}
    return get_columns(filters), get_data(filters)


# ---------------------- COLUMNS ----------------------
def get_columns(filters):

    month = filters.get("month")

    return [
        {"label": "Customer Group", "fieldname": "customer_group", "width": 160},
        {"label": "Customer", "fieldname": "customer", "width": 240},
        {
            "label": f"{month} Sales",
            "fieldname": "month_amount",
            "fieldtype": "HTML",
            "width": 140
        },
        {
            "label": "Total",
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 140
        }
    ]


# ---------------------- DATA ----------------------
def get_data(filters):

    month_no = MONTH_MAP[filters.get("month")]
    customer_group = filters.get("customer_group")

    conditions = ""
    values = [month_no]   # ✅ ONLY ONE PLACEHOLDER

    if customer_group:
        conditions += " AND customer_group = %s"
        values.append(customer_group)

    sql = f"""
        SELECT
            customer_group,
            customer,
            SUM(grand_total) AS total,
            SUM(
                CASE 
                    WHEN MONTH(posting_date) = %s THEN grand_total
                    ELSE 0
                END
            ) AS month_amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        {conditions}
        GROUP BY customer
        ORDER BY customer
    """

    rows = frappe.db.sql(sql, values, as_dict=True)

    data = []

    for r in rows:
        data.append({
            "customer_group": r.customer_group,
            "customer": r.customer,
            "month_amount_raw": r.month_amount,
            "month_amount": f"""
                <a href="#"
                   class="month-amount"
                   data-customer="{r.customer}">
                   {frappe.utils.fmt_money(r.month_amount)}
                </a>
            """,
            "total": r.total
        })

    return data


# ---------------------- DRILLDOWN POPUP ----------------------
@frappe.whitelist()
def get_invoice_drilldown(customer, month, customer_group=None):

    month_no = MONTH_MAP[month]

    conditions = ""
    values = [customer, month_no]

    if customer_group:
        conditions += " AND customer_group = %s"
        values.append(customer_group)

    sql = f"""
        SELECT
            name,
            posting_date,
            grand_total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND customer = %s
          AND MONTH(posting_date) = %s
          {conditions}
        ORDER BY posting_date
    """

    rows = frappe.db.sql(sql, values, as_dict=True)

    if not rows:
        return "<b>No Sales Invoices found</b>"

    html = """
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Sales Invoice</th>
                    <th>Posting Date</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    for r in rows:
        html += f"""
            <tr>
                <td>
                    <a href="/app/sales-invoice/{r.name}" target="_blank">
                        {r.name}
                    </a>
                </td>
                <td>{r.posting_date}</td>
                <td>{frappe.utils.fmt_money(r.grand_total)}</td>
            </tr>
        """

    html += "</tbody></table>"

    return html
