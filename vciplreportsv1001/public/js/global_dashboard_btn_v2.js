console.log("✅ global_dashboard_btn_v3.js loaded");

const REQUIRED_ROLE = "Dashboard Manager";

// ASSETS
const DASHBOARD_LOGO = "/assets/vciplreportsv1001/images/dashboard_logo.png";
const BACK_LOGO = "/assets/vciplreportsv1001/images/back.png";

function userHasDashboardAccess() {
  return frappe.user_roles && frappe.user_roles.includes(REQUIRED_ROLE);
}

function renderDashboardButton() {

  document.querySelectorAll(".dashboard-btn-global").forEach(el => el.remove());
  if (!userHasDashboardAccess()) return;

  const isReportDashboard = frappe.get_route()?.[0] === "report-dashboard";

  const btn = document.createElement("button");
  btn.className = "dashboard-btn-global";

  // BASE BUTTON STYLE
  btn.style.cssText = `
    position: fixed;
    right: 18px;
    top: 50%;
    transform: translateY(-50%);
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    z-index: 10000;
    box-shadow: 0 8px 20px rgba(0,0,0,.35);
    transition: transform .25s ease, box-shadow .25s ease;
    background-repeat: no-repeat;
    background-position: center;
    background-size: 60%;
    background-color: #111;
  `;

  // SET IMAGE AS BACKGROUND
  if (isReportDashboard) {
    btn.style.backgroundImage = `url(${BACK_LOGO})`;
    btn.title = "Back to Accounting";
  } else {
    btn.style.backgroundImage = `url(${DASHBOARD_LOGO})`;
    btn.title = "Open Report Dashboard";
  }

  // HOVER EFFECT
  btn.onmouseenter = () => {
    btn.style.transform = "translateY(-50%) scale(1.1)";
    btn.style.boxShadow = "0 12px 28px rgba(0,0,0,.45)";
  };
  btn.onmouseleave = () => {
    btn.style.transform = "translateY(-50%) scale(1)";
    btn.style.boxShadow = "0 8px 20px rgba(0,0,0,.35)";
  };

  // CLICK ACTION
  btn.onclick = () => {
    if (isReportDashboard) {
      frappe.set_route("accounting"); // ✅ correct route
    } else {
      frappe.set_route("report-dashboard");
    }
  };

  document.body.appendChild(btn);
}

frappe.after_ajax(renderDashboardButton);
frappe.router.on("change", renderDashboardButton);
