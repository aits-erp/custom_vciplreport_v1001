console.log("✅ global_dashboard_btn.js loaded");

// 🔐 ONLY THIS ROLE CAN SEE THE BUTTON
const REQUIRED_ROLE = "Dashboard Manager";

function userHasDashboardAccess() {
  return (
    frappe.user_roles &&
    frappe.user_roles.includes(REQUIRED_ROLE)
  );
}

function renderDashboardButton() {

  // ❌ Remove button if user doesn't have role
  if (!userHasDashboardAccess()) {
    document
      .querySelectorAll(".dashboard-btn-global")
      .forEach(el => el.remove());
    return;
  }

  const route = frappe.get_route();
  const isReportDashboard = route && route[0] === "report-dashboard";

  // Remove existing button
  document
    .querySelectorAll(".dashboard-btn-global")
    .forEach(el => el.remove());

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
    fontSize: "22px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  });

  if (isReportDashboard) {
    // 🔙 BACK → Accounting Workspace
    btn.innerText = "⬅";
    btn.title = "Back to Accounting";

    btn.onclick = () => {
      frappe.set_route("workspace", "Accounting");
    };

  } else {
    // 📊 OPEN DASHBOARD
    btn.innerText = "📊";
    btn.title = "Open Report Dashboard";

    btn.onclick = () => {
      frappe.set_route("report-dashboard");
    };
  }

  document.body.appendChild(btn);
}

// Initial render
frappe.after_ajax(() => {
  renderDashboardButton();
});

// Re-render on route change
frappe.router.on("change", () => {
  renderDashboardButton();
});
