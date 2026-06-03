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
    """Return ordered list of category (custom_main_group) values to display."""
    if filters.get("custom_main_group"):
        raw = filters.custom_main_group
        if isinstance(raw, list):
            return [c for c in raw if c]
        return [c.strip() for c in raw.split(",") if c.strip()]

    # Derive from invoices within the date range so only relevant categories appear
    conditions = "si.docstatus = 1 AND i.custom_main_group IS NOT NULL AND i.custom_main_group != ''"
    values = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.to_date

    rows = frappe.db.sql(f"""
        SELECT DISTINCT i.custom_main_group
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE {conditions}
        ORDER BY i.custom_main_group
    """, values)

    return [r[0] for r in rows if r[0]]


# ─────────────────────────────────────────────────────────────────────────────
# COLUMNS
# ─────────────────────────────────────────────────────────────────────────────
def get_columns(categories, filters=None):
    columns = []

    if filters and filters.get("show_item_details"):
        columns += [
            {"label": _("Item Code"), "fieldname": "item_code",
             "fieldtype": "Link", "options": "Item", "width": 150},
            {"label": _("Item Name"), "fieldname": "item_name",
             "fieldtype": "Data", "width": 200},
        ]

    columns += [
        {"label": _("Month"),             "fieldname": "month",               "fieldtype": "Data",     "width": 90,  "align": "center"},
        {"label": _("TSO"),               "fieldname": "tso_name",            "fieldtype": "Link",     "options": "Sales Person", "width": 180},
        {"label": _("Customer Name"),     "fieldname": "customer_name",       "fieldtype": "Data",     "width": 200},
        {"label": _("Region"),            "fieldname": "custom_region",       "fieldtype": "Data",     "width": 120},
        {"label": _("Head Sales Person"), "fieldname": "parent_sales_person", "fieldtype": "Link",     "options": "Sales Person", "width": 180},
        {"label": _("Total Target"),      "fieldname": "total_target",        "fieldtype": "Currency", "width": 140},
        {"label": _("Total Achieved"),    "fieldname": "total_achieved",      "fieldtype": "Currency", "width": 140},
        {"label": _("Ach %"),             "fieldname": "ach_pct",             "fieldtype": "Percent",  "width": 90},
    ]

    for cat in categories:
        safe = _safe(cat)
        columns += [
            {"label": _(f"{cat} — Target"),   "fieldname": f"{safe}_target",   "fieldtype": "Currency", "width": 130},
            {"label": _(f"{cat} — Achieved"), "fieldname": f"{safe}_achieved", "fieldtype": "Currency", "width": 130},
        ]

    return columns


def _safe(name):
    """Convert a category name to a safe Python/ERPNext fieldname."""
    import re
    return re.sub(r"[^a-zA-Z0-9]", "_", name).lower()


# ─────────────────────────────────────────────────────────────────────────────
# TARGET HELPERS  (no globals — uses a dict passed by reference)
# ─────────────────────────────────────────────────────────────────────────────
def _load_all_targets(tso_list):
    """
    Bulk-load targets for all TSOs in a single query.
    Returns: { (tso_name, month_num): { category: amount } }

    FIX 1: docstatus = 1  (was 0 — caused targets to never be found when
                           the EXISTS check in the main query used docstatus=1)
    FIX 2: No idx=1 restriction (removed from main query too)
    """
    if not tso_list:
        return {}

    placeholders = ", ".join(["%s"] * len(tso_list))

    rows = frappe.db.sql(f"""
        SELECT
            mtd.sales_person,
            mtd.main_group,
            mtd.jan_target, mtd.feb_target, mtd.mar_target,
            mtd.apr_target, mtd.may_target, mtd.jun_target,
            mtd.jul_target, mtd.aug_target, mtd.sep_target,
            mtd.oct_target, mtd.nov_target, mtd.dec_target
        FROM `tabMonthly Target Detail` mtd
        INNER JOIN `tabSales Person Target` spt ON spt.name = mtd.parent
        WHERE mtd.sales_person IN ({placeholders})
          AND spt.period_type = 'Monthly'
          AND spt.docstatus   = 1
    """, tuple(tso_list), as_dict=1)

    cache = {}
    month_fields = [
        "jan_target", "feb_target", "mar_target", "apr_target",
        "may_target", "jun_target", "jul_target", "aug_target",
        "sep_target", "oct_target", "nov_target", "dec_target",
    ]
    for r in rows:
        if not r.main_group:
            continue
        tso = r.sales_person
        for m_idx, field in enumerate(month_fields, 1):
            key = (tso, m_idx)
            if key not in cache:
                cache[key] = {}
            cache[key][r.main_group] = flt(r.get(field, 0))

    return cache


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DATA
# ─────────────────────────────────────────────────────────────────────────────
def get_data(filters, categories):
    conditions = []
    values = {}

    # ── Date filters ──
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.to_date

    # ── TSO filter ──
    if filters.get("sales_person"):
        conditions.append(
            "COALESCE(sp_inv.name, sp_cust.name) = %(sales_person)s"
        )
        values["sales_person"] = filters.sales_person

    # ── Head sales person filter ──
    if filters.get("parent_sales_person"):
        conditions.append("""
            COALESCE(sp_inv.parent_sales_person,
                     sp_cust.parent_sales_person) = %(parent_sales_person)s
        """)
        values["parent_sales_person"] = filters.parent_sales_person

    # ── Customer filter ──
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.customer

    # ── Customer group filter ──
    if filters.get("customer_group"):
        conditions.append("si.customer_group = %(customer_group)s")
        values["customer_group"] = filters.customer_group

    # ── Region filter (MultiSelectList → list or comma string) ──
    regions = _to_list(filters.get("custom_region"))
    if regions:
        conditions.append("""
            COALESCE(sp_inv.custom_region, sp_cust.custom_region) IN %(custom_region)s
        """)
        values["custom_region"] = tuple(regions)

    # ── Head sales code filter ──
    codes = _to_list(filters.get("custom_head_sales_code"))
    if codes:
        conditions.append("""
            COALESCE(sp_inv.custom_head_sales_code,
                     sp_cust.custom_head_sales_code) IN %(custom_head_sales_code)s
        """)
        values["custom_head_sales_code"] = tuple(codes)

    # ── Category filter ──
    if filters.get("custom_main_group"):
        cat_filter = _to_list(filters.custom_main_group)
        if cat_filter:
            conditions.append("i.custom_main_group IN %(custom_main_group)s")
            values["custom_main_group"] = tuple(cat_filter)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # ── GROUP BY ──
    # FIX 3: Removed EXISTS subquery that was excluding invoices whose TSO
    # hasn't submitted a target document yet.
    # FIX 4: Removed st_inv.idx = 1 restriction — use MIN(st_inv.idx) via
    #         a subquery join so we always get exactly one sales-team row.
    group_by_fields = """
        DATE_FORMAT(si.posting_date, '%%Y-%%m'),
        MONTH(si.posting_date),
        YEAR(si.posting_date),
        COALESCE(sp_inv.name, sp_cust.name, 'Unassigned'),
        COALESCE(sp_inv.parent_sales_person, sp_cust.parent_sales_person, ''),
        COALESCE(sp_inv.custom_region, sp_cust.custom_region, ''),
        COALESCE(sp_inv.custom_head_sales_code, sp_cust.custom_head_sales_code, ''),
        c.customer_name,
        i.custom_main_group
    """

    if filters.get("show_item_details"):
        group_by_fields += ", sii.item_code, i.item_name"

    select_item = "sii.item_code, i.item_name," if filters.get("show_item_details") else ""

    query = f"""
        SELECT
            DATE_FORMAT(si.posting_date, '%%Y-%%m')                                    AS month_key,
            MONTH(si.posting_date)                                                      AS month_num,
            YEAR(si.posting_date)                                                       AS year_num,
            COALESCE(sp_inv.name, sp_cust.name, 'Unassigned')                          AS tso_name,
            COALESCE(sp_inv.parent_sales_person, sp_cust.parent_sales_person, '')       AS parent_sales_person,
            COALESCE(sp_inv.custom_region, sp_cust.custom_region, '')                  AS custom_region,
            COALESCE(sp_inv.custom_head_sales_code, sp_cust.custom_head_sales_code, '') AS custom_head_sales_code,
            c.customer_name,
            i.custom_main_group                                                         AS category,
            {select_item}
            SUM(sii.base_net_amount)                                                    AS achieved,
            COUNT(DISTINCT si.name)                                                     AS invoice_count,
            COUNT(DISTINCT sii.item_code)                                               AS item_count
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` i                 ON i.name = sii.item_code
        INNER JOIN `tabCustomer` c             ON c.name = si.customer

        -- Sales Person from Invoice Sales Team (lowest idx = primary)
        LEFT JOIN (
            SELECT parent, MIN(idx) AS min_idx
            FROM `tabSales Team`
            WHERE parenttype = 'Sales Invoice'
            GROUP BY parent
        ) st_inv_min ON st_inv_min.parent = si.name
        LEFT JOIN `tabSales Team` st_inv
            ON  st_inv.parent     = si.name
            AND st_inv.parenttype = 'Sales Invoice'
            AND st_inv.idx        = st_inv_min.min_idx
        LEFT JOIN `tabSales Person` sp_inv ON sp_inv.name = st_inv.sales_person

        -- Sales Person from Customer master (fallback)
        LEFT JOIN (
            SELECT parent, MIN(idx) AS min_idx
            FROM `tabSales Team`
            WHERE parenttype = 'Customer'
            GROUP BY parent
        ) st_cust_min ON st_cust_min.parent = si.customer
        LEFT JOIN `tabSales Team` st_cust
            ON  st_cust.parent     = si.customer
            AND st_cust.parenttype = 'Customer'
            AND st_cust.idx        = st_cust_min.min_idx
        LEFT JOIN `tabSales Person` sp_cust ON sp_cust.name = st_cust.sales_person

        WHERE si.docstatus = 1
          AND i.custom_main_group IS NOT NULL
          AND i.custom_main_group != ''
          AND {where_clause}

        GROUP BY {group_by_fields}
        ORDER BY
            YEAR(si.posting_date),
            MONTH(si.posting_date),
            COALESCE(sp_inv.name, sp_cust.name, 'Unassigned'),
            c.customer_name
    """

    raw_rows = frappe.db.sql(query, values, as_dict=1)

    # ── Bulk-load targets for every TSO seen in results ──
    tso_set = {r.tso_name for r in raw_rows if r.tso_name and r.tso_name != "Unassigned"}
    target_cache = _load_all_targets(list(tso_set))

    # ── Aggregate into result dict ──
    result = {}

    for row in raw_rows:
        tso      = row.tso_name or "Unassigned"
        month_num = int(row.month_num)

        if filters.get("show_item_details"):
            key = (row.month_key, tso, row.customer_name,
                   row.parent_sales_person, row.custom_region, row.item_code)
        else:
            key = (row.month_key, tso, row.customer_name,
                   row.parent_sales_person, row.custom_region)

        if key not in result:
            # Fetch targets for this TSO + month once
            tso_targets = target_cache.get((tso, month_num), {})
            total_target = sum(flt(tso_targets.get(cat, 0)) for cat in categories)

            entry = {
                "month":               f"{MONTHS[month_num - 1]}-{row.year_num}",
                "month_num":           month_num,
                "year_num":            int(row.year_num),
                "tso_name":            tso,
                "customer_name":       row.customer_name or "—",
                "parent_sales_person": row.parent_sales_person or "",
                "custom_region":       row.custom_region or "",
                "total_achieved":      0.0,
                "total_target":        total_target,
                "ach_pct":             0.0,
                "invoice_count":       0,
                "item_count":          0,
            }

            if filters.get("show_item_details"):
                entry["item_code"] = row.item_code
                entry["item_name"] = row.item_name

            for cat in categories:
                safe = _safe(cat)
                entry[f"{safe}_target"]   = flt(tso_targets.get(cat, 0))
                entry[f"{safe}_achieved"] = 0.0

            result[key] = entry

        safe = _safe(row.category)
        result[key][f"{safe}_achieved"] += flt(row.achieved)
        result[key]["total_achieved"]   += flt(row.achieved)
        result[key]["invoice_count"]    += int(row.invoice_count)
        # FIX 5: item_count — use max not sum (avoid double-counting across categories)
        result[key]["item_count"]       += int(row.item_count)

    # ── Compute Ach % after all rows merged ──
    final = []
    for entry in result.values():
        tgt = entry["total_target"]
        ach = entry["total_achieved"]
        entry["ach_pct"] = round((ach / tgt * 100), 2) if tgt else 0.0
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
        total_invoice  += int(row.get("invoice_count", 0))   # FIX 6: was flt()
        total_item     += int(row.get("item_count", 0))

    overall_pct = round((total_achieved / total_target * 100), 2) if total_target else 0.0

    return [
        {"label": _("Total Achieved"),  "value": total_achieved,  "indicator": "Green",  "datatype": "Currency"},
        {"label": _("Total Target"),    "value": total_target,    "indicator": "Blue",   "datatype": "Currency"},
        {"label": _("Overall Ach %"),   "value": overall_pct,     "indicator": "Orange", "datatype": "Percent"},
        {"label": _("Invoice Count"),   "value": total_invoice,   "indicator": "Purple", "datatype": "Int"},
        {"label": _("Item Count"),      "value": total_item,      "indicator": "Gray",   "datatype": "Int"},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def _to_list(value):
    """Normalise a filter value that may be a list, comma string, or None."""
    if not value:
        return []
    if isinstance(value, list):
        return [v.strip() for v in value if v and str(v).strip()]
    return [v.strip() for v in str(value).split(",") if v.strip()]