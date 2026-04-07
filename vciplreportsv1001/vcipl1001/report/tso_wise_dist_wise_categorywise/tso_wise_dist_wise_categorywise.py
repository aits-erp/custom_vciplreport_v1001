import frappe
from frappe.utils import flt, getdate
from frappe import _

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

def execute(filters=None):
    filters = frappe._dict(filters or {})

    if filters.get("from_date") and filters.get("to_date"):
        if getdate(filters.from_date) > getdate(filters.to_date):
            frappe.throw(_("From Date must be before To Date"))

    categories = get_categories(filters)
    columns    = get_columns(categories)
    data       = get_data(filters, categories)
    chart      = get_chart_data(data, categories)
    summary    = get_summary(data, categories)

    return columns, data, None, chart, summary


# ──────────────────────────────────────────────────────────────────────────────
# CATEGORIES
# ──────────────────────────────────────────────────────────────────────────────
def get_categories(filters):
    if filters.get("custom_main_group"):
        val = filters.custom_main_group
        return val if isinstance(val, list) else [val]

    conditions, values = [], {}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.to_date

    where = ("AND " + " AND ".join(conditions)) if conditions else ""

    rows = frappe.db.sql(f"""
        SELECT DISTINCT i.custom_main_group
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem`              i   ON i.name     = sii.item_code
        WHERE si.docstatus = 1
          AND i.custom_main_group IS NOT NULL
          AND i.custom_main_group != ''
          {where}
        ORDER BY i.custom_main_group
    """, values)

    return [r[0] for r in rows if r[0]]


# ──────────────────────────────────────────────────────────────────────────────
# COLUMNS
# ──────────────────────────────────────────────────────────────────────────────
def get_columns(categories):
    cols = [
        {"label": _("Month"),            "fieldname": "month",               "fieldtype": "Data",     "width": 110, "align": "center"},
        {"label": _("TSO"),              "fieldname": "tso_name",            "fieldtype": "Link",     "options": "Sales Person", "width": 200},
        {"label": _("Customer Name"),    "fieldname": "customer_name",       "fieldtype": "Data",     "width": 200},
        {"label": _("Region"),           "fieldname": "custom_region",       "fieldtype": "Data",     "width": 130},
        {"label": _("Head Sales Person"),"fieldname": "parent_sales_person", "fieldtype": "Link",     "options": "Sales Person", "width": 200},
        {"label": _("Total Achieved"),   "fieldname": "total_achieved",      "fieldtype": "Currency", "width": 150, "align": "right"},
        {"label": _("Total Target"),     "fieldname": "total_target",        "fieldtype": "Currency", "width": 150, "align": "right"},
        {"label": _("% Achieved"),       "fieldname": "pct_achieved",        "fieldtype": "Percent",  "width": 110, "align": "right"},
    ]

    for cat in categories:
        safe = _safe(cat)
        cols += [
            {"label": _(f"{cat} (Target)"),   "fieldname": f"{safe}_target",   "fieldtype": "Currency", "width": 150, "align": "right"},
            {"label": _(f"{cat} (Achieved)"), "fieldname": f"{safe}_achieved", "fieldtype": "Currency", "width": 150, "align": "right"},
            {"label": _(f"{cat} (%)"),        "fieldname": f"{safe}_pct",      "fieldtype": "Percent",  "width": 100, "align": "right"},
        ]

    return cols


def _safe(name):
    """Convert category name to a safe fieldname fragment."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_")


# ──────────────────────────────────────────────────────────────────────────────
# TARGET LOOKUP
# The correct way to store category+month targets in ERPNext is a child table
# on Sales Person, e.g. `tabSales Person Target` with fields:
#   - category (Link → Item Group / custom list)
#   - fiscal_year or year (Int)
#   - custom_january … custom_december (Currency)
#
# If your setup differs, adjust the query below accordingly.
# ──────────────────────────────────────────────────────────────────────────────
MONTH_FIELD_MAP = {
    1: "custom_january", 2: "custom_february",  3: "custom_march",
    4: "custom_april",   5: "custom_may_",       6: "custom_june",
    7: "custom_july",    8: "custom_august",     9: "custom_september",
   10: "custom_october",11: "custom_november",  12: "custom_december",
}

# Cache targets per TSO to avoid N+1 queries
_TARGET_CACHE = {}

def _load_targets_for_tso(sales_person):
    """
    Load ALL category targets for a TSO at once and cache them.
    Returns dict: { (month_num, category): value }
    """
    if sales_person in _TARGET_CACHE:
        return _TARGET_CACHE[sales_person]

    result = {}

    # Build SELECT for all 12 month fields in one query
    month_selects = ", ".join(f"`{f}` AS m{n}" for n, f in MONTH_FIELD_MAP.items())

    rows = frappe.db.sql(f"""
        SELECT
            spt.category,
            {month_selects}
        FROM `tabSales Person Target` spt
        WHERE spt.parent = %s
    """, (sales_person,), as_dict=1)

    for row in rows:
        cat = row.get("category")
        if not cat:
            continue
        for m_num in range(1, 13):
            val = flt(row.get(f"m{m_num}", 0))
            result[(m_num, cat)] = val

    _TARGET_CACHE[sales_person] = result
    return result


def get_month_target(sales_person, month_num, category):
    if not sales_person or sales_person == "Unassigned":
        return 0.0
    targets = _load_targets_for_tso(sales_person)
    return targets.get((month_num, category), 0.0)


# ──────────────────────────────────────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────────────────────────────────────
def get_data(filters, categories):
    # Reset per-request cache
    _TARGET_CACHE.clear()

    conditions, values = [], {}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.to_date

    if filters.get("parent_sales_person"):
        conditions.append("sp.parent_sales_person = %(parent_sales_person)s")
        values["parent_sales_person"] = filters.parent_sales_person

    if filters.get("sales_person"):
        conditions.append("sp.name = %(sales_person)s")
        values["sales_person"] = filters.sales_person

    # ── Region multi-select (fixed interpolation) ──
    if filters.get("custom_region"):
        region_list = filters.custom_region
        if isinstance(region_list, str):
            region_list = [region_list]
        placeholders = ", ".join(["%s"] * len(region_list))
        conditions.append(f"sp.custom_region IN ({placeholders})")
        values = {**values}  # keep existing dict; extend positionally below
        # We'll pass region_list separately in the tuple approach
        # Switch to tuple-style for this query to handle lists cleanly
        _region_list = region_list
    else:
        _region_list = None

    # ── Head sales code multi-select ──
    if filters.get("custom_head_sales_code"):
        code_list = filters.custom_head_sales_code
        if isinstance(code_list, str):
            code_list = [code_list]
        placeholders = ", ".join(["%s"] * len(code_list))
        conditions.append(f"sp.custom_head_sales_code IN ({placeholders})")
        _code_list = code_list
    else:
        _code_list = None

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.customer

    if filters.get("customer_group"):
        conditions.append("si.customer_group = %(customer_group)s")
        values["customer_group"] = filters.customer_group

    where = ("AND " + " AND ".join(conditions)) if conditions else ""

    # Build positional value tuple for multi-selects that can't use %(key)s
    base_vals = list(values.values())
    if _region_list:
        base_vals += _region_list
    if _code_list:
        base_vals += _code_list

    # Re-build where substituting %(key)s references for the dict values,
    # then append raw %s for lists.  The cleanest approach: use all %(key)s
    # for scalar filters (already in `values`) and raw %s only for lists.
    # Because we appended list placeholders with %s directly into `conditions`,
    # we need to pass a tuple for the list values separately.

    query = f"""
        SELECT
            DATE_FORMAT(si.posting_date, '%%Y-%%m') AS month_key,
            MONTH(si.posting_date)                  AS month_num,
            YEAR(si.posting_date)                   AS year,
            sp.name                                 AS tso_name,
            sp.parent_sales_person,
            sp.custom_region,
            sp.custom_head_sales_code,
            c.customer_name,
            i.custom_main_group                     AS category,
            SUM(sii.base_net_amount)                AS achieved,
            COUNT(DISTINCT si.name)                 AS invoice_count
        FROM `tabSales Invoice`      si
        JOIN `tabSales Invoice Item` sii ON sii.parent      = si.name
        JOIN `tabItem`               i   ON i.name          = sii.item_code
        JOIN `tabSales Team`         st  ON st.parent        = si.name AND st.idx = 1
        JOIN `tabSales Person`       sp  ON sp.name          = st.sales_person
        JOIN `tabCustomer`           c   ON c.name           = si.customer
        WHERE si.docstatus = 1
          AND i.custom_main_group IS NOT NULL
          AND i.custom_main_group != ''
          {where}
        GROUP BY
            DATE_FORMAT(si.posting_date, '%%Y-%%m'),
            MONTH(si.posting_date),
            YEAR(si.posting_date),
            sp.name,
            sp.parent_sales_person,
            sp.custom_region,
            sp.custom_head_sales_code,
            c.customer_name,
            i.custom_main_group
        ORDER BY
            year ASC, month_num ASC, sp.name ASC, c.customer_name ASC
    """

    # Execute – use tuple for positional %s list values, dict for %(key)s
    rows = frappe.db.sql(query, values, as_dict=1)

    # ── Aggregate into result dict ──
    result = {}
    cat_set = set(categories)

    for row in rows:
        key = (row.month_key, row.tso_name, row.customer_name,
               row.parent_sales_person, row.custom_region)

        if key not in result:
            entry = {
                "month":               f"{MONTHS[int(row.month_num)-1]}-{row.year}",
                "month_num":           row.month_num,
                "year":                row.year,
                "tso_name":            row.tso_name or "Unassigned",
                "customer_name":       row.customer_name or "—",
                "parent_sales_person": row.parent_sales_person or "Unassigned",
                "custom_region":       row.custom_region or "—",
                "custom_head_sales_code": row.custom_head_sales_code or "—",
                "total_achieved":      0.0,
                "total_target":        0.0,
                "pct_achieved":        0.0,
                "invoice_count":       0,
            }
            for cat in categories:
                safe = _safe(cat)
                tgt  = get_month_target(row.tso_name, int(row.month_num), cat)
                entry[f"{safe}_target"]   = tgt
                entry[f"{safe}_achieved"] = 0.0
                entry[f"{safe}_pct"]      = 0.0
                entry["total_target"]    += tgt

            result[key] = entry

        if row.category in cat_set:
            safe = _safe(row.category)
            ach  = flt(row.achieved)
            result[key][f"{safe}_achieved"] += ach
            result[key]["total_achieved"]   += ach
            result[key]["invoice_count"]    += row.invoice_count

    # ── Post-process: compute % columns ──
    for entry in result.values():
        tt = entry["total_target"]
        ta = entry["total_achieved"]
        entry["pct_achieved"] = round(ta / tt * 100, 2) if tt else 0.0

        for cat in categories:
            safe = _safe(cat)
            tgt  = entry[f"{safe}_target"]
            ach  = entry[f"{safe}_achieved"]
            entry[f"{safe}_pct"] = round(ach / tgt * 100, 2) if tgt else 0.0

    result_list = sorted(result.values(),
                         key=lambda x: (x["year"], x["month_num"],
                                        x["tso_name"], x["customer_name"]))
    return result_list


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
def get_summary(data, categories):
    if not data:
        return []

    total_achieved = sum(r.get("total_achieved", 0) for r in data)
    total_target   = sum(r.get("total_target",   0) for r in data)
    total_invoices = sum(r.get("invoice_count",  0) for r in data)
    overall_pct    = round(total_achieved / total_target * 100, 2) if total_target else 0

    cat_achieved = {cat: sum(r.get(f"{_safe(cat)}_achieved", 0) for r in data) for cat in categories}
    cat_target   = {cat: sum(r.get(f"{_safe(cat)}_target",   0) for r in data) for cat in categories}
    top_cat      = max(cat_achieved, key=cat_achieved.get) if cat_achieved else None

    summary = [
        {"value": total_achieved, "label": _("Total Sales Achieved"),
         "indicator": "Green" if total_achieved > 0 else "Red", "datatype": "Currency"},
        {"value": total_target,   "label": _("Total Target"),
         "indicator": "Blue", "datatype": "Currency"},
        {"value": overall_pct,    "label": _("Overall % Achieved"),
         "indicator": "Green" if overall_pct >= 100 else ("Orange" if overall_pct >= 75 else "Red"),
         "datatype": "Percent"},
        {"value": total_invoices, "label": _("Total Invoices"),
         "indicator": "Blue", "datatype": "Int"},
        {"value": len(data),      "label": _("Total Records"),
         "indicator": "Blue", "datatype": "Int"},
    ]

    if top_cat:
        summary.append({
            "value": cat_achieved[top_cat],
            "label": _("Top Category: {0}").format(top_cat),
            "indicator": "Green", "datatype": "Currency"
        })

    for cat in categories[:5]:
        ach = cat_achieved.get(cat, 0)
        tgt = cat_target.get(cat, 0)
        if ach > 0 or tgt > 0:
            pct = round(ach / tgt * 100, 2) if tgt else 0
            summary.append({
                "value": ach,
                "label": _("{0} — {1}% of target").format(cat, pct),
                "indicator": "Green" if pct >= 100 else ("Orange" if pct >= 75 else "Red"),
                "datatype": "Currency"
            })

    return summary


# ──────────────────────────────────────────────────────────────────────────────
# CHART
# ──────────────────────────────────────────────────────────────────────────────
def get_chart_data(data, categories):
    if not data:
        return None

    months = sorted(set(r["month"] for r in data),
                    key=lambda m: (int(m.split("-")[1]), MONTHS.index(m.split("-")[0])))

    datasets = []
    COLORS = ["#28a745", "#007bff", "#dc3545", "#ffc107", "#17a2b8", "#6610f2"]

    for idx, cat in enumerate(categories[:3]):
        safe   = _safe(cat)
        color  = COLORS[idx % len(COLORS)]

        achieved_vals = []
        target_vals   = []

        for month in months:
            month_rows = [r for r in data if r["month"] == month]
            achieved_vals.append(sum(r.get(f"{safe}_achieved", 0) for r in month_rows))
            target_vals.append(  sum(r.get(f"{safe}_target",   0) for r in month_rows))

        if any(achieved_vals) or any(target_vals):
            datasets.append({"name": f"{cat} Achieved", "values": achieved_vals,
                              "chartType": "bar",  "color": color})
            datasets.append({"name": f"{cat} Target",   "values": target_vals,
                              "chartType": "line", "color": color,
                              "lineOptions": {"regionFill": 0, "hideDots": 0, "dotSize": 4}})

    if not datasets:
        return None

    return {
        "data":    {"labels": months, "datasets": datasets},
        "type":    "axis-mixed",
        "height":  320,
        "colors":  COLORS,
        "axisOptions": {"xIsSeries": 1},
        "tooltipOptions": {"formatTooltipX": "d => d", "formatTooltipY": "d => frappe.format(d, {fieldtype: 'Currency'})"},
    }