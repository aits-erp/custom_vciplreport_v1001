frappe.provide("frappe.views");

// Use the router change event to ensure we catch the class after it loads dynamically
frappe.router.on('change', function() {
    // Check if QueryReport class exists and hasn't been patched by us yet
    if (frappe.views.QueryReport && !frappe.views.QueryReport.prototype._custom_export_patched) {
        
        // Override the standard core export function
        frappe.views.QueryReport.prototype.export_report = function() {
            const report = this;
            
            // Get current filters. If mandatory filters are missing, get_values() handles the alert and returns false
            const filters = report.get_values();
            if (!filters) return; 

            // Construct standard URL params
            const params = new URLSearchParams({
                report_name: report.report_name,
                filters: JSON.stringify(filters)
            });

            // Route directly to your custom API
            const url = `/api/method/vcipl1001.api.export.export_query?${params.toString()}`;
            
            // Open in new tab to trigger the binary download safely
            window.open(url, "_blank");
        };

        // Mark as patched so we don't re-apply it unnecessarily
        frappe.views.QueryReport.prototype._custom_export_patched = true;
        console.log("🔥 VCIPL: Global Query Report Export intercepted successfully.");
    }
});