# Copyright (c) 2023, Raaj tailor and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta, datetime

class AttendanceMissout(Document):
	@frappe.whitelist()
	def miss_out(self):
		cond = get_condition(self)
		attendance = frappe.db.sql("""
			select
			a.name
			from `tabAttendance` a
			where
			a.miss_in_out = 1
			{condition}
			""".format(condition = cond), as_dict = True)

		for att in attendance:
			att_doc = frappe.get_doc("Attendance",att.name)
			notification = frappe.get_doc("Notification","Attendance Miss Out Aler")
			notification.send(att_doc)
		
		
		return attendance

	@frappe.whitelist()
	def absent_miss_out(self):
		cond = get_condition(self)
		attendance = frappe.db.sql("""
		select
		a.*,
		e.personal_email
		from `tabAttendance` a,
		`tabEmployee` e
		where
		e.name = a.employee
		and
		a.miss_in_out <> 1
		and
		a.status = 'Absent'
		{condition}
		""".format(condition = cond),as_dict = True)
		
		return attendance
	
def get_condition(self):
	date = datetime.strptime(self.date, '%Y-%m-%d').date()
	
	cond = ""
	if date.day < 17:
		date_in = (date - timedelta(days=2))
		cond = "and a.attendance_date = '{date}'".format(date = date_in)
	else:
		from_date = date.replace(day=1)
		cond = "and a.attendance_date between '{from_dt}' and '{to_date}'".format(from_dt = from_date, to_date = date)

	return cond