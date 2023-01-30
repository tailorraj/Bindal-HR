# Copyright (c) 2023, Raaj tailor and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_employees_data(filters)
	
	return columns, data

def get_columns(filters):
	columns=[
		{
			"label":_("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"width": "180",
			"options": "employee"
		},
		{
			"label":_("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": "180",
		},
		{
			"label":_("Late_entry_count"),
			"fieldname":"late_entry_count",
			"fieldtype": "Int",
			"width": "150",
		},
		{
			"label":_("Early_exit_count"),
			"fieldname":"early_exit",
			"fieldtype": "Int",
			"width": "150",
		},
	]
	return columns

def get_employees_data(filters):
	fromdate = filters.from_date
	todate = filters.to_date

	emp_data = frappe.db.sql("""SELECT employee,employee_name,
	if((select count(*) from `tabAttendance` 
	where late_entry = 1 and employee = emp.name
                        and attendance_date BETWEEN '{fromdate}' and '{todate}' group by employee) is not null,(select count(*) from `tabAttendance` 
	where late_entry = 1 and employee = emp.name
                        and attendance_date BETWEEN '{fromdate}' and '{todate}' group by employee),0) as late_entry_count,
	if((select count(*) from `tabAttendance` 
	where early_exit = 1 and employee = emp.name
                        and attendance_date BETWEEN '{fromdate}' and '{todate}' group by employee) is not null,(select count(*) from `tabAttendance` 
	where early_exit = 1 and employee = emp.name
                        and attendance_date BETWEEN '{fromdate}' and '{todate}' group by employee),0) as early_exit
                        FROM `tabEmployee` emp where status = 'Active'
            """.format(fromdate = fromdate,todate=todate),as_dict=1)
	result = []
	for row in emp_data:
		if not (row.early_exit == 0 and row.late_entry_count == 0):
			result.append(row)

	return result

