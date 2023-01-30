# Copyright (c) 2023, Raaj tailor and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now
from frappe.model.document import Document

class GatePass(Document):
	def validate(self):
		count = frappe.db.sql("select count(name) as cou from `tabGate Pass` where year(out_time) = year(CAST(STR_TO_DATE(%s, '%%Y-%%m-%%d') AS DATE)) and month(out_time) = month(CAST(STR_TO_DATE(%s, '%%Y-%%m-%%d') AS DATE)) and employee = %s", (self.out_time, self.out_time, self.employee), as_dict = True)
		# frappe.msgprint(self.out_time)
		# frappe.msgprint(self.employee)
		# frappe.msgprint(str(count[0].cou))

		if count[0].cou > 2:
			frappe.msgprint("Gate Pass Exceed Entry: 2")