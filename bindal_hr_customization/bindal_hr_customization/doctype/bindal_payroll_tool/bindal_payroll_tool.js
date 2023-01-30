// Copyright (c) 2023, Raaj tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bindal Payroll Tool', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__("Get Employees"), function() {
			frm.trigger("get_employee");
		}).toggleClass('btn-primary', !(frm.doc.component || []).length);
	},

	start_date: function (frm) {
		// frm.trigger("reset");
		if(frm.doc.start_date){
			
			frm.trigger("set_end_date");
			frm.set_value("tool_item",[])
			frm.refresh_field("tool_item")
		}
	},
	set_end_date: function(frm){
		frappe.call({
			method: 'erpnext.payroll.doctype.payroll_entry.payroll_entry.get_end_date',
			args: {
				frequency: "Monthly",
				start_date: frm.doc.start_date
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('end_date', r.message.end_date);
				}
			}
		});
	},
	get_employee:function(frm){
		if(frm.doc.start_date && frm.doc.end_date){
			frm.set_value("tool_item",[])
			frm.refresh_field("tool_item")
			return frappe.call({
				doc: frm.doc,
				method: 'fill_employee',
				callback: function(r) {
					console.log(r)
					console.log(r.message)
					if (r.docs[0].tool_item){
						frm.dirty()
					}
					refresh_field("tool_item")
				}
			})
		}else{
			frappe.throw("Please select Start and End Date First!")
		}
		
	}

});
