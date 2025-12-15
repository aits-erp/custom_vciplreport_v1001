console.log("✅ global_dashboard_btn.js loaded");

function renderDashboardButton() {

  const route = frappe.get_route();
  const isReportDashboard = route && route[0] === "report-dashboard";

  // remove existing button
  document.querySelectorAll(".dashboard-btn-global").forEach(el => el.remove());

  const btn = document.createElement("button");
  btn.className = "dashboard-btn-global";

  Object.assign(btn.style, {
    position: "fixed",
    right: "15px",
    top: "50%",
    transform: "translateY(-50%)",
    width: "56px",
    height: "56px",
    borderRadius: "50%",
    border: "none",
    background: "#ffffff",
    boxShadow: "0 6px 16px rgba(0,0,0,0.25)",
    cursor: "pointer",
    zIndex: "10000",
    fontSize: "20px"
  });

  if (isReportDashboard) {
    // 🔙 BACK → Accounting
    btn.innerText = "⬅";
    btn.title = "Back to Accounting";

    btn.onclick = () => {
      frappe.set_route("accounting");
    };

  } else {
    // 📊 DASHBOARD
    btn.innerText = "📊";
    btn.title = "Open Report Dashboard";

    btn.onclick = () => {
      frappe.set_route("report-dashboard");
    };
  }

  document.body.appendChild(btn);
}

// initial render
frappe.after_ajax(() => {
  renderDashboardButton();
});

// update on route change
frappe.router.on("change", () => {
  renderDashboardButton();
});
