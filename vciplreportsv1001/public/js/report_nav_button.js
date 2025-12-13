frappe.ready(function () {

    console.log("VCIPL Report Nav Button Loaded");

    // Wait till navbar loads
    $(document).on("toolbar_setup", function () {
        add_report_nav_button();
    });

});

function add_report_nav_button() {

    // Prevent duplicate button
    if ($("#vcipl-report-btn").length) return;

    // Add button in navbar
    let btn = `
        <li class="nav-item">
            <a class="nav-link" id="vcipl-report-btn" href="/app/report-dashboard">
                📊 Reports Dashboard
            </a>
        </li>
    `;

    $(".navbar-nav").append(btn);
}
