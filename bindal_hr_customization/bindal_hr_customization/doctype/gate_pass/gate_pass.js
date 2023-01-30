// Copyright (c) 2023, Raaj tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gate Pass', {
		// validate: function(frm) {
		// 	dateToday = new Date()
		// 	console.log(dateToday)
		// },
	out_time: function(frm){
		if(frm.doc.expected_in_time){
			var entry_datetime = cur_frm.doc.out_time.split(" ")[1];
			var exit_datetime = cur_frm.doc.expected_in_time.split(" ")[1];

			var hour=0;
			var minute=0;

			var splitEntryDatetime= entry_datetime.split(':');
			var splitExitDatetime= exit_datetime.split(':');
			if (cur_frm.doc.out_time > cur_frm.doc.expected_in_time ){
				frappe.throw("Out Time Is After Expected In Time")
			}
			else{
			
			hour = Math.abs(parseInt(splitExitDatetime[0])-parseInt(splitEntryDatetime[0]));
			minute = Math.abs(parseInt(splitExitDatetime[1]) - parseInt(splitEntryDatetime[1]));
			hour = hour + minute/60;
			minute = minute%60;
			var dur = (hour*60)+minute
			console.log(dur)
			frm.doc.duration = dur
			refresh_field("duration")
			}
		}
	},
	expected_in_time: function(frm){
		if(frm.doc.out_time){
			var entry_datetime = cur_frm.doc.out_time.split(" ")[1];
			var exit_datetime = cur_frm.doc.expected_in_time.split(" ")[1];

			var hour=0;
			var minute=0;

			var splitEntryDatetime= entry_datetime.split(':');
			var splitExitDatetime= exit_datetime.split(':');
			if (cur_frm.doc.out_time > cur_frm.doc.expected_in_time ){
				frappe.throw("Out Time Is After Expected In Time")
			}else{
			hour = Math.abs(parseInt(splitExitDatetime[0])-parseInt(splitEntryDatetime[0]));
			minute = Math.abs(parseInt(splitExitDatetime[1]) - parseInt(splitEntryDatetime[1]));
			hour = hour + minute/60;
			minute = minute%60;
			var dur = (hour*60)+minute
			console.log(dur)
			frm.doc.duration = dur
			refresh_field("duration")
			}
		}
	}
});
