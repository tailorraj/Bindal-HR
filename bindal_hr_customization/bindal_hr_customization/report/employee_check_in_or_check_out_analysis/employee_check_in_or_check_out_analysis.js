// Copyright (c) 2023, Raaj tailor and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Check In or Check Out Analysis"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "180",
			"options": "Company",
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "late_entry_count" && data && data.late_entry_count > 2) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		if (column.fieldname == "early_exit" && data && data.early_exit > 2) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		// else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
		// 	value = "<span style='color:green'>" + value + "</span>";
		// }

		return value;
	}

	// "formatter": function (value, row, column, data, default_formatter) {
	// 	value = default_formatter(value, row, column, data);

	// 	if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
	// 		value = "<span style='color:red'>" + value + "</span>";
	// 	}
	// 	else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
	// 		value = "<span style='color:green'>" + value + "</span>";
	// 	}

	// 	return value;
	// }
};
