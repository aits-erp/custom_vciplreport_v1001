console.log("vciplreportsv1001 desk.js loaded");

frappe.ready(function () {
    frappe.ui.toolbar.add_icon("chart", function () {
        frappe.set_route("report-dashboard");
    }, __("Report Dashboard"));
});
