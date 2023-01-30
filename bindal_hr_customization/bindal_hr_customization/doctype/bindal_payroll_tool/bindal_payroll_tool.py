# Copyright (c) 2023, Raaj tailor and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff
from datetime import datetime

class BindalPayrollTool(Document):
	def validate(self):
		pass
	def on_submit(self):
		if self.tool_item:
			add_salary_comp = frappe.get_doc('Bindal payroll Component Setup')		
			if add_salary_comp.extra_deduct and add_salary_comp.holiday_comp:
				for comp in self.tool_item:
					#holiday component creation
					self.create_component(comp.employee,comp.incentive,comp.name,add_salary_comp.holiday_comp)					
					self.create_component(comp.employee,comp.extra_salary_deduction,comp.name,add_salary_comp.extra_deduct)
			else:
				frappe.throw("First Set values in Payroll Component Setup")							
		else:
			frappe.throw("Employee List is Empty")


	def create_component(self,employee,value,row_name,component):
		if value > 0 and not frappe.db.get_value('Additional Salary',{'employee':employee,'salary_component':component,
		'payroll_date':self.start_date},'name'):		
			company = frappe.db.get_value('Employee', employee, 'company')
			additional_salary = frappe.new_doc('Additional Salary')
			additional_salary.employee = employee
			additional_salary.bindal_payroll_ref = self.name
			additional_salary.salary_component = component
			additional_salary.amount = value
			additional_salary.payroll_date = self.start_date
			additional_salary.company = company
			additional_salary.bindal_payroll_tool = self.name
			additional_salary.bindal_payroll_child_table_reference = row_name
			additional_salary.save()
			frappe.msgprint("Salary Component created for "+employee)
	
	@frappe.whitelist()		
	def fill_employee(self):
		self.set('tool_item', [])		
		employees = frappe.db.sql("""select distinct t1.name as employee, t1.employee_name
		from `tabEmployee` t1, 
		`tabSalary Structure Assignment` t2 where t1.name = t2.employee """, as_dict=True)

		if not employees:
			frappe.throw(_("No employees for the mentioned criteria"))		

		for d in employees:

			self.append('tool_item', d)	
		
		return d
	