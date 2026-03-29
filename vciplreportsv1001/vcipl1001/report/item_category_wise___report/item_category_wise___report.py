import frappe
from frappe.utils import flt
import json


def execute(filters=None):
    filters = frappe._dict(filters or {})

    data, customers = get_pivot_data(filters)
    columns = get_columns(customers)

    return columns, data


# ---------------------------------------------------------
# COLUMNS
# ---------------------------------------------------------
def get_columns(customers):

    columns = [
        {"label": "Item Group", "fieldname": "item_group", "width": 180},
        {"label": "Main Group", "fieldname": "custom_main_group", "width": 180},
        {"label": "Sub Group", "fieldname": "custom_sub_group", "width": 180},
    ]

    for customer in customers:
        columns.append({
            "label": customer,
            "fieldname": frappe.scrub(customer),
            "fieldtype": "Currency",
            "width": 150
        })

    # hidden popup data column
    columns.append({
        "fieldname": "popup_data",
        "hidden": 1
    })

    # hidden row index for JS reference
    columns.append({
        "fieldname": "idx",
        "hidden": 1
    })

    return columns


# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
def get_pivot_data(filters):

    conditions = ""
    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.customer:
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.customer

    if filters.item_group:
        conditions += " AND i.item_group = %(item_group)s"
        values["item_group"] = filters.item_group

    if filters.custom_main_group:
        conditions += " AND i.custom_main_group = %(custom_main_group)s"
        values["custom_main_group"] = filters.custom_main_group

    if filters.custom_sub_group:
        conditions += " AND i.custom_sub_group = %(custom_sub_group)s"
        values["custom_sub_group"] = filters.custom_sub_group

    if filters.custom_item_type:
        conditions += " AND i.custom_item_type = %(custom_item_type)s"
        values["custom_item_type"] = filters.custom_item_type

    if filters.parent_sales_person:
        conditions += " AND sp.parent_sales_person = %(parent_sales_person)s"
        values["parent_sales_person"] = filters.parent_sales_person

    raw_data = frappe.db.sql(
        f"""
        SELECT
            i.item_group,
            i.custom_main_group,
            i.custom_sub_group,
            c.customer_name,
            sii.item_name,
            sii.qty,
            sii.base_net_amount AS amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        JOIN `tabCustomer` c ON c.name = si.customer
        LEFT JOIN `tabSales Team` st
            ON st.parent = si.name AND st.parenttype = 'Sales Invoice'
        LEFT JOIN `tabSales Person` sp ON sp.name = st.sales_person
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        """,
        values,
        as_dict=True
    )

    # ---------------------------------------------
    # Identify unique customers
    # ---------------------------------------------
    customers = sorted({row.customer_name for row in raw_data})

    result = {}

    # ---------------------------------------------
    # Build pivot structure
    # ---------------------------------------------
    for row in raw_data:

        item_group = row.item_group or "Undefined"
        main_group = row.custom_main_group or "Undefined"
        sub_group = row.custom_sub_group or "Undefined"
        customer = row.customer_name

        key = f"{item_group}::{main_group}::{sub_group}"
        cust_field = frappe.scrub(customer)

        if key not in result:
            result[key] = {
                "item_group": item_group,
                "custom_main_group": main_group,
                "custom_sub_group": sub_group,
                "popup_data": {}
            }

            # initialize pivot columns
            for c in customers:
                sc = frappe.scrub(c)
                result[key][sc] = 0
                result[key]["popup_data"][sc] = {}

        # -------------------------
        # Add pivot amount
        # -------------------------
        result[key][cust_field] += flt(row.amount)

        # -------------------------
        # Add popup item breakdown
        # -------------------------
        items = result[key]["popup_data"][cust_field]

        if row.item_name not in items:
            items[row.item_name] = {
                "item_name": row.item_name,
                "qty": 0,
                "amount": 0
            }

        items[row.item_name]["qty"] += flt(row.qty)
        items[row.item_name]["amount"] += flt(row.amount)

    # ---------------------------------------------
    # Convert popup dict → list + add totals
    # ---------------------------------------------
    data = []

    for record in result.values():

        for cust in record["popup_data"]:
            item_list = list(record["popup_data"][cust].values())

            total_qty = sum(i["qty"] for i in item_list)
            total_amt = sum(i["amount"] for i in item_list)

            item_list.append({
                "item_name": "Total",
                "qty": total_qty,
                "amount": total_amt
            })

            record["popup_data"][cust] = item_list

        # Convert to JSON string for JS
        record["popup_data"] = json.dumps(record["popup_data"])

        data.append(record)

    # ---------------------------------------------
    # Add Row Index (for JS safe popup reference)
    # ---------------------------------------------
    for idx, row in enumerate(data, start=1):
        row["idx"] = idx

    return data, customers
