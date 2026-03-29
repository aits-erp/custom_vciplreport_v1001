import frappe

@frappe.whitelist()
def get_dashboard_data(from_date=None, to_date=None, company=None, sales_person=None, region=None):

    conditions = " AND si.docstatus = 1"

    if from_date and to_date:
        conditions += f" AND si.posting_date BETWEEN '{from_date}' AND '{to_date}'"

    if company:
        conditions += f" AND si.company = '{company}'"

    if sales_person:
        conditions += f" AND st.sales_person = '{sales_person}'"

    if region:
        conditions += f" AND st.custom_region = '{region}'"

    data = frappe.db.sql(f"""
        SELECT
            st.sales_person,
            st.custom_region,
            sii.item_group,
            SUM(sii.base_net_amount) as achieved

        FROM `tabSales Invoice` si

        LEFT JOIN `tabSales Invoice Item` sii
            ON sii.parent = si.name

        LEFT JOIN `tabSales Team` st
            ON st.parent = si.name

        WHERE 1=1 {conditions}

        GROUP BY
            st.sales_person,
            st.custom_region,
            sii.item_group
    """, as_dict=1)

    # ================= KPI =================
    total_achieved = sum([d.achieved for d in data])
    total_target = total_achieved * 1.2  # replace later

    percent = (total_achieved / total_target * 100) if total_target else 0

    return {
        "kpi": {
            "target": total_target,
            "achieved": total_achieved,
            "percent": percent
        },
        "data": data
    }