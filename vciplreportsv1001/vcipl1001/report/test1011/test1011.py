import frappe
from frappe.utils import flt, getdate
from frappe import _

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MONTH_FIELD_MAP = {
    1:  "jan_target",
    2:  "feb_target",
    3:  "mar_target",
    4:  "apr_target",
    5:  "may_target",
    6:  "jun_target",
    7:  "jul_target",
    8:  "aug_target",
    9:  "sep_target",
    10: "oct_target",
    11: "nov_target",
    12: "dec_target",
}


def execute(filters=None):
    filters = frappe._dict(filters or {})

    if filters.get("from_date") and filters.get("to_date"):
        if getdate(filters.from_date) > getdate(filters.to_date):
            frappe.throw(_("From Date must be before To Date"))

    categories = get_categories(filters)
    columns    = get_columns(categories, filters)
    data       = get_data(filters, categories)
    summary    = get_summary(data, categories)

    return columns, data, None, None, summary


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
def get_categories(filters):
    if filters.get("custom_main_group"):
        raw = filters.custom_main_group
        if isinstance(raw, list):
            return [c for c in raw if c]
        return [c.strip() for c in raw.split(",") if c.strip()]

    conditions = ""
    values = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.to_date

    rows = frappe.db.sql("""
        SELECT DISTINCT i.custom_main_group
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE si.docstatus = 1
          AND i.custom_main_group IS NOT NULL
          AND i.custom_main_group != ''
          {conditions}
        ORDER BY i.custom_main_group
    """.format(conditions=conditions), values)

    return [r[0] for r in rows if r[0]]


# ─────────────────────────────────────────────────────────────────────────────
# COLUMNS
# ─────────────────────────────────────────────────────────────────────────────
def get_columns(categories, filters=None):
    columns = []

    if filters and filters.get("show_item_details"):
        columns.extend([
            {"label": _("Item Code"), "fieldname": "item_code",
             "fieldtype": "Link", "options": "Item", "width": 150},
            {"label": _("Item Name"), "fieldname": "item_name",
             "fieldtype": "Data", "width": 200},
        ])

    columns.extend([
        {"label": _("Month"),             "fieldname": "month",               "fieldtype": "Data",     "width": 100, "align": "center"},
        {"label": _("TSO"),               "fieldname": "tso_name",            "fieldtype": "Link",     "options": "Sales Person", "width": 200},
        {"label": _("Customer Name"),     "fieldname": "customer_name",       "fieldtype": "Data",     "width": 200},
        {"label": _("Region"),            "fieldname": "custom_region",       "fieldtype": "Data",     "width": 150},
        {"label": _("Head Sales Person"), "fieldname": "parent_sales_person", "fieldtype": "Link",     "options": "Sales Person", "width": 200},
        {"label": _("Total Target"),      "fieldname": "total_target",        "fieldtype": "Currency", "width": 150},
        {"label": _("Total Achieved"),    "fieldname": "total_achieved",      "fieldtype": "Currency", "width": 150},
        {"label": _("Ach %"),             "fieldname": "ach_pct",             "fieldtype": "Percent",  "width": 90},
    ])

    for cat in categories:
        safe = _safe(cat)
        columns.append({"label": _(f"{cat} (Target)"),   "fieldname": f"{safe}_target",   "fieldtype": "Currency", "width": 130})
        columns.append({"label": _(f"{cat} (Achieved)"), "fieldname": f"{safe}_achieved", "fieldtype": "Currency", "width": 130})

    return columns


def _safe(name):
    return name.replace(" ", "_").replace("-", "_")


# ─────────────────────────────────────────────────────────────────────────────
# TARGET CACHE  (your original approach — kept, just cleaned up)
# ─────────────────────────────────────────────────────────────────────────────
_target_cache = {}


def _load_targets_for_tso(tso_name, month_num):
    cache_key = (tso_name, int(month_num))          # FIX: always int key
    if cache_key in _target_cache:
        return _target_cache[cache_key]

    month_field = MONTH_FIELD_MAP.get(int(month_num), "jan_target")

    try:
        rows = frappe.db.sql(f"""
            SELECT
                mtd.main_group,
                mtd.{month_field} AS target_amount
            FROM `tabMonthly Target Detail` mtd
            INNER JOIN `tabSales Person Target` spt
                ON spt.name = mtd.parent
            WHERE mtd.sales_person = %(tso_name)s
              AND spt.period_type  = 'Monthly'
              AND spt.docstatus    IN (0, 1)
        """, {"tso_name": tso_name}, as_dict=1)

        result = {r.main_group: flt(r.target_amount) for r in rows if r.main_group}
        _target_cache[cache_key] = result
        return result

    except Exception as e:
        frappe.log_error(f"Target fetch error for {tso_name}: {e}", "TSO Report")

    _target_cache[cache_key] = {}
    return {}


def get_month_target_from_sales_team(tso_name, month_num, category):
    targets = _load_targets_for_tso(tso_name, month_num)
    return flt(targets.get(category, 0))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DATA
# ─────────────────────────────────────────────────────────────────────────────
def get_data(filters, categories):
    global _target_cache
    _target_cache = {}                              # reset per request

    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.to_date

    if filters.get("sales_person"):
        conditions.append("COALESCE(sp_inv.name, sp_cust.name) = %(sales_person)s")
        values["sales_person"] = filters.sales_person

    if filters.get("parent_sales_person"):
        conditions.append("""
            COALESCE(sp_inv.parent_sales_person,
                     sp_cust.parent_sales_person) = %(parent_sales_person)s
        """)
        values["parent_sales_person"] = filters.parent_sales_person

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.customer

    if filters.get("customer_group"):
        conditions.append("si.customer_group = %(customer_group)s")
        values["customer_group"] = filters.customer_group

    regions = _to_list(filters.get("custom_region"))
    if regions:
        conditions.append("""
            COALESCE(sp_inv.custom_region, sp_cust.custom_region) IN %(custom_region)s
        """)
        values["custom_region"] = tuple(regions)

    codes = _to_list(filters.get("custom_head_sales_code"))
    if codes:
        conditions.append("""
            COALESCE(sp_inv.custom_head_sales_code,
                     sp_cust.custom_head_sales_code) IN %(custom_head_sales_code)s
        """)
        values["custom_head_sales_code"] = tuple(codes)

    cat_filter = _to_list(filters.get("custom_main_group"))
    if cat_filter:
        conditions.append("i.custom_main_group IN %(custom_main_group)s")
        values["custom_main_group"] = tuple(cat_filter)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    group_by = """
        DATE_FORMAT(si.posting_date, '%%Y-%%m'),
        MONTH(si.posting_date),
        YEAR(si.posting_date),
        COALESCE(sp_inv.name, sp_cust.name, 'Unassigned'),
        COALESCE(sp_inv.parent_sales_person, sp_cust.parent_sales_person, ''),
        COALESCE(sp_inv.custom_region, sp_cust.custom_region, ''),
        c.customer_name,
        i.custom_main_group
    """

    if filters.get("show_item_details"):
        group_by += ", sii.item_code, i.item_name"

    query = f"""
        SELECT
            DATE_FORMAT(si.posting_date, '%%Y-%%m')                         AS month_key,
            MONTH(si.posting_date)                                           AS month_num,
            YEAR(si.posting_date)                                            AS year,
            COALESCE(sp_inv.name, sp_cust.name, 'Unassigned')               AS tso_name,
            COALESCE(sp_inv.parent_sales_person,
                     sp_cust.parent_sales_person, '')                        AS parent_sales_person,
            COALESCE(sp_inv.custom_region, sp_cust.custom_region, '')       AS custom_region,
            c.customer_name,
            i.custom_main_group                                              AS category,
            sii.item_code,
            i.item_name,
            SUM(sii.base_net_amount)                                         AS achieved,
            COUNT(DISTINCT si.name)                                          AS invoice_count,
            COUNT(DISTINCT sii.item_code)                                    AS item_count

        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i                 ON i.name = sii.item_code
        INNER JOIN `tabCustomer` c             ON c.name = si.customer

        LEFT JOIN `tabSales Team` st_inv
            ON  st_inv.parent     = si.name
            AND st_inv.parenttype = 'Sales Invoice'
            AND st_inv.idx        = 1
        LEFT JOIN `tabSales Person` sp_inv ON sp_inv.name = st_inv.sales_person

        LEFT JOIN `tabSales Team` st_cust
            ON  st_cust.parent     = si.customer
            AND st_cust.parenttype = 'Customer'
        LEFT JOIN `tabSales Person` sp_cust ON sp_cust.name = st_cust.sales_person

        WHERE si.docstatus = 1
          AND i.custom_main_group IS NOT NULL
          AND i.custom_main_group != ''
          AND EXISTS (
              SELECT 1
              FROM `tabMonthly Target Detail` mtd
              INNER JOIN `tabSales Person Target` spt ON spt.name = mtd.parent
              WHERE mtd.sales_person = COALESCE(sp_inv.name, sp_cust.name)
                AND spt.period_type  = 'Monthly'
                AND spt.docstatus    IN (0, 1)
          )
          AND {where_clause}

        GROUP BY {group_by}

        ORDER BY
            YEAR(si.posting_date),
            MONTH(si.posting_date),
            COALESCE(sp_inv.name, sp_cust.name, 'Unassigned'),
            c.customer_name
    """

    raw_data = frappe.db.sql(query, values, as_dict=1)
    result = {}

    for row in raw_data:
        tso = row.tso_name or "Unassigned"

        if filters.get("show_item_details"):
            key = (row.month_key, tso, row.customer_name,
                   row.parent_sales_person, row.custom_region, row.item_code)
        else:
            key = (row.month_key, tso, row.customer_name,
                   row.parent_sales_person, row.custom_region)

        if key not in result:
            entry = {
                "month":               f"{MONTHS[int(row.month_num) - 1]}-{row.year}",
                "month_num":           int(row.month_num),
                "year":                row.year,
                "tso_name":            tso,
                "customer_name":       row.customer_name or "No Customer",
                "parent_sales_person": row.parent_sales_person or "",
                "custom_region":       row.custom_region or "",
                "total_achieved":      0.0,
                "total_target":        0.0,
                "ach_pct":             0.0,
                "invoice_count":       0,
                "item_count":          0,
            }

            if filters.get("show_item_details"):
                entry["item_code"] = row.item_code
                entry["item_name"] = row.item_name

            for cat in categories:
                safe = _safe(cat)
                target_val = get_month_target_from_sales_team(tso, row.month_num, cat)
                entry[f"{safe}_target"]   = flt(target_val)
                entry[f"{safe}_achieved"] = 0.0
                entry["total_target"]    += flt(target_val)

            result[key] = entry

        safe = _safe(row.category)
        result[key][f"{safe}_achieved"] += flt(row.achieved)
        result[key]["total_achieved"]   += flt(row.achieved)
        result[key]["invoice_count"]    += int(row.invoice_count)
        result[key]["item_count"]       += int(row.item_count)

    # Compute Ach % after all rows are merged
    final = []
    for entry in result.values():
        tgt = entry["total_target"]
        ach = entry["total_achieved"]
        entry["ach_pct"] = round(ach / tgt * 100, 2) if tgt else 0.0
        final.append(entry)

    return final


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
def get_summary(data, categories):
    total_achieved = total_target = 0.0
    total_invoice  = total_item   = 0

    for row in data:
        total_achieved += flt(row.get("total_achieved"))
        total_target   += flt(row.get("total_target"))
        total_invoice  += int(row.get("invoice_count", 0))
        total_item     += int(row.get("item_count", 0))

    overall_pct = round(total_achieved / total_target * 100, 2) if total_target else 0.0

    return [
        {"label": _("Total Achieved"), "value": total_achieved, "indicator": "Green",  "datatype": "Currency"},
        {"label": _("Total Target"),   "value": total_target,   "indicator": "Blue",   "datatype": "Currency"},
        {"label": _("Overall Ach %"),  "value": overall_pct,    "indicator": "Orange", "datatype": "Percent"},
        {"label": _("Invoice Count"),  "value": total_invoice,  "indicator": "Purple", "datatype": "Int"},
        {"label": _("Item Count"),     "value": total_item,     "indicator": "Gray",   "datatype": "Int"},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def _to_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return [v.strip() for v in value if v and str(v).strip()]
    return [v.strip() for v in str(value).split(",") if v.strip()]