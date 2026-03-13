frappe.query_reports["CATEGORYWISE"] = {
    filters: [

        {
            fieldname: "fiscal_year",
            label: "Fiscal Year",
            fieldtype: "Link",
            options: "Fiscal Year",
            default: frappe.defaults.get_user_default("fiscal_year"),
            reqd: 1
        },

        {
            fieldname: "custom_main_group",
            label: "Main Group",
            fieldtype: "Select",
            options: `
Hard Anodised
Nonstick
Horeca
Pressure Cookers
SS Cookware
Healux
Kraft
Platinum
Platinum Triply P.cooker
Cast Iron
Bottle
Kraft Pressure Cooker
Electrical Appliances
Csd
Raw Material
Scrap
Cookers Spare Parts
Circle
Other Spare
Carton
SFG
Sticker & Warranty Card
Trading SFG
Machinery Spare Parts
`
        },

        {
            fieldname: "parent_sales_person",
            label: "Parent Sales Person",
            fieldtype: "Link",
            options: "Sales Person"
        }

    ]
};