frappe.pages['mis-dashboard'].on_page_load = function(wrapper) {

	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'MIS Dashboard',
		single_column: true
	});

	// ============================
	// 🔹 FILTERS
	// ============================

	let from_date = page.add_field({
		label: 'From Date',
		fieldtype: 'Date',
		fieldname: 'from_date',
		default: frappe.datetime.month_start()
	});

	let to_date = page.add_field({
		label: 'To Date',
		fieldtype: 'Date',
		fieldname: 'to_date',
		default: frappe.datetime.month_end()
	});

	let sales_person = page.add_field({
		label: 'Sales Person',
		fieldtype: 'Link',
		options: 'Sales Person'
	});

	let region = page.add_field({
		label: 'Region',
		fieldtype: 'Data'   // change to Link if you create Region DocType
	});

	page.set_primary_action('Load Dashboard', () => {
		load_data();
	});

	// ============================
	// 🔹 UI STRUCTURE
	// ============================

	$(page.body).html(`
		<div id="kpi-section" style="display:flex; gap:20px; margin-top:20px;"></div>
		<div id="chart-section" style="margin-top:30px;"></div>
		<div id="table-section" style="margin-top:30px;"></div>
	`);

	// ============================
	// 🔹 LOAD DATA
	// ============================

	function load_data() {
		frappe.call({
			method: "vciplreportsv1001.vcipl1001.api.mis_dashboard.get_dashboard_data",
			args: {
				from_date: from_date.get_value(),
				to_date: to_date.get_value(),
				sales_person: sales_person.get_value(),
				region: region.get_value()
			},
			callback: function(r) {
				if (r.message) {
					render_kpi(r.message.kpi);
					render_chart(r.message.data);
					render_table(r.message.data);
				}
			}
		});
	}

	// ============================
	// 🔹 KPI CARDS
	// ============================

	function render_kpi(kpi) {
		$("#kpi-section").html(`
			<div class="card" style="padding:20px; background:#f5f7fa;">
				<h4>Target</h4>
				<h2>${kpi.target.toFixed(2)}</h2>
			</div>

			<div class="card" style="padding:20px; background:#e6f7ff;">
				<h4>Achieved</h4>
				<h2>${kpi.achieved.toFixed(2)}</h2>
			</div>

			<div class="card" style="padding:20px; background:#fff7e6;">
				<h4>Achievement %</h4>
				<h2>${kpi.percent.toFixed(2)}%</h2>
			</div>
		`);
	}

	// ============================
	// 🔹 CHART
	// ============================

	function render_chart(data) {

		let grouped = {};

		data.forEach(d => {
			if (!grouped[d.item_group]) {
				grouped[d.item_group] = 0;
			}
			grouped[d.item_group] += d.achieved;
		});

		let labels = Object.keys(grouped);
		let values = Object.values(grouped);

		$("#chart-section").html('<div id="chart"></div>');

		new frappe.Chart("#chart", {
			data: {
				labels: labels,
				datasets: [{
					values: values
				}]
			},
			type: 'bar',
			height: 300
		});
	}

	// ============================
	// 🔹 TABLE
	// ============================

	function render_table(data) {

		let html = `
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>Sales Person</th>
						<th>Region</th>
						<th>Category</th>
						<th>Achieved</th>
					</tr>
				</thead>
				<tbody>
		`;

		data.forEach(d => {
			html += `
				<tr>
					<td>${d.sales_person || ""}</td>
					<td>${d.custom_region || ""}</td>
					<td>${d.item_group || ""}</td>
					<td>${d.achieved || 0}</td>
				</tr>
			`;
		});

		html += `</tbody></table>`;

		$("#table-section").html(html);
	}

};