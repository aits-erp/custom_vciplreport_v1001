frappe.query_reports["Customer Sales Target vs Achievement"] = {

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data || !column.fieldname.endsWith("_ach")) return value;

        let month = column.fieldname.replace("_ach", "");
        let drill = JSON.parse(data.ach_drill || "{}");

        if (!drill[month]) return value;

        return `<a href="#" class="ach-drill" data-invoices="${drill[month]}">${value}</a>`;
    },

    onload: function () {
        $(document).on("click", ".ach-drill", function (e) {
            e.preventDefault();

            let invoices = $(this).data("invoices").split(",");

            frappe.msgprint({
                title: "Invoices",
                message: invoices.join("<br>"),
                indicator: "blue"
            });
        });
    }
};
