import frappe
from frappe.utils import today, getdate, date_diff


def execute(filters=None):
    return get_columns(), get_data(filters)


# --------------------------------------------------
# COLUMNS
# --------------------------------------------------
def get_columns():
    return [
        {"label": "Customer Group", "fieldname": "customer_group",
         "fieldtype": "Link", "options": "Customer Group", "width": 160},

        {"label": "RSM", "fieldname": "rsm",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "ASM", "fieldname": "asm",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "TSO", "fieldname": "tso",
         "fieldtype": "Link", "options": "Sales Person", "width": 150},

        {"label": "Total Outstanding", "fieldname": "total_outstanding",
         "fieldtype": "Currency", "width": 160},

        # 🔥 ACHIEVEMENT (HIDDEN BY DEFAULT – JS WILL TOGGLE)
        {"label": "Total Achieved", "fieldname": "total_achieved",
         "fieldtype": "Currency", "width": 160, "hidden": 1},

        {"label": "Jan Achieved", "fieldname": "jan_achieved",
         "fieldtype": "Currency", "width": 140, "hidden": 1},

        {"label": "Feb Achieved", "fieldname": "feb_achieved",
         "fieldtype": "Currency", "width": 140, "hidden": 1},

        # 🔥 DRILL HELPERS
        {"label": "Total Ach Drill", "fieldname": "total_ach_drill", "hidden": 1},
        {"label": "Jan Ach Drill", "fieldname": "jan_ach_drill", "hidden": 1},
        {"label": "Feb Ach Drill", "fieldname": "feb_ach_drill", "hidden": 1},
    ]


# --------------------------------------------------
# DATA
# --------------------------------------------------
def get_data(filters=None):

    invoices = frappe.db.sql("""
        SELECT
            si.name,
            si.customer,
            si.customer_group,
            si.posting_date,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
    """, as_dict=True)

    data_map = {}

    for inv in invoices:
        key = inv.customer_group

        if key not in data_map:
            data_map[key] = {
                "customer_group": key,
                "total_outstanding": 0,
                "total_achieved": 0,
                "jan_achieved": 0,
                "feb_achieved": 0,
                "total_ach_drill": [],
                "jan_ach_drill": [],
                "feb_ach_drill": [],
            }

        amt = inv.grand_total
        month = getdate(inv.posting_date).month

        data_map[key]["total_achieved"] += amt
        data_map[key]["total_ach_drill"].append({
            "invoice": inv.name,
            "date": str(inv.posting_date),
            "amount": amt
        })

        if month == 1:
            data_map[key]["jan_achieved"] += amt
            data_map[key]["jan_ach_drill"].append({
                "invoice": inv.name,
                "date": str(inv.posting_date),
                "amount": amt
            })

        if month == 2:
            data_map[key]["feb_achieved"] += amt
            data_map[key]["feb_ach_drill"].append({
                "invoice": inv.name,
                "date": str(inv.posting_date),
                "amount": amt
            })

    result = []

    for row in data_map.values():
        result.append({
            "customer_group": row["customer_group"],
            "total_outstanding": row["total_outstanding"],
            "total_achieved": row["total_achieved"],
            "jan_achieved": row["jan_achieved"],
            "feb_achieved": row["feb_achieved"],
            "total_ach_drill": frappe.as_json(row["total_ach_drill"]),
            "jan_ach_drill": frappe.as_json(row["jan_ach_drill"]),
            "feb_ach_drill": frappe.as_json(row["feb_ach_drill"]),
        })

    return result
