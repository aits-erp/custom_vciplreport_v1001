frappe.query_reports["Customer Sales Target vs Achievement"] = {

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Make Sales Person clickable
        if (column.fieldname === "sales_person" && data.customer_drill) {
            return `<a href="#" class="sp-drill"
                        data-customers='${data.customer_drill}'>
                        ${value}
                    </a>`;
        }

        return value;
    },

    onload: function () {

        $(document).on("click", ".sp-drill", function (e) {
            e.preventDefault();

            let customers = [];

            try {
                customers = JSON.parse($(this).attr("data-customers"));
            } catch (err) {
                console.error(err);
            }

            if (!customers.length) {
                frappe.msgprint("No customers tagged with this Sales Person");
                return;
            }

            frappe.msgprint({
                title: "Customers Tagged",
                message: customers.join("<br>"),
                indicator: "blue"
            });
        });
    }
};
