// Copyright (c) 2023, Raaj tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Missout', {
	refresh: function(frm) {
		frm.add_custom_button(__('Miss Out'), function(){
			frappe.call({
				method: 'miss_out',
				doc: frm.doc,
				freeze: true,
				callback: (r) => {
					// on success
					console.log(r)
					
					var str_out = ""
					for(var i in r.message){
						str_out += r.message[i]["attendance_date"] + ", "
					}
					frm.doc.output = str_out
					refresh_field("output")
				},
				error: (r) => {
					// on error
				}
			})
		}, __("Utilities"));

		frm.add_custom_button(__('ABS Miss Out'), function(){
			frappe.call({
				method: 'absent_miss_out',
				doc: frm.doc,
				freeze: true,
				callback: (r) => {
					// on success
					console.log(r)
					
					var str_out = ""
					for(var i in r.message){
						str_out += r.message[i]["attendance_date"] + ", "
					}
					frm.doc.output = str_out
					refresh_field("output")
				},
				error: (r) => {
					// on error
				}
			})
		}, __("Utilities"));
	}
});
