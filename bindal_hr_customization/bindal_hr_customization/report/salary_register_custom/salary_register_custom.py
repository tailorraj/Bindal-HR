# Copyright (c) 2023, Raaj tailor and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt,date_diff
from datetime import datetime

import erpnext
from datetime import datetime
# from bindal_hr_customization.bindal_hr_customization.doctype.bindal_payroll_tool.bindal_payroll_tool import get_monthly_present,get_salary_details,get_gross_and_basic_salary
import itertools

def execute(filters=None):
	if not filters: filters = {}
	currency = None
	if filters.get('currency'):
		currency = filters.get('currency')
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips: return [], []

	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
	doj_map = get_employee_doj_map()

	data = []
	for ss in salary_slips:
		row = [ss.name, ss.employee, ss.employee_name, doj_map.get(ss.employee), ss.branch, ss.department, ss.designation,
			ss.company, ss.start_date, ss.end_date, ss.leave_without_pay, ss.payment_days]

		if ss.branch is not None: columns[3] = columns[3].replace('-1','120')
		if ss.department is not None: columns[4] = columns[4].replace('-1','120')
		if ss.designation is not None: columns[5] = columns[5].replace('-1','120')
		if ss.leave_without_pay is not None: columns[9] = columns[9].replace('-1','130')


		for e in earning_types:

			row.append(ss_earning_map.get(ss.name, {}).get(e))

		if currency == company_currency:
			row += [(flt(ss.gross_pay) * flt(ss.exchange_rate))]
		else:
			row += [(int(ss.gross_pay))]
	# -------------------------Custom Logic for 3 component--------------------
		bonus_provision = 0
		leave_reimbursement_provision = 0
		Leave = int(ss.absent_days)

		monthly_present,total_days,bonus_days,ssa_gross = get_leave_and_bonus(ss.employee, ss.start_date, ss.end_date,ss.absent_days)
		bonus_rate = frappe.get_value('Employee',ss.employee,'bonus')
		basic = int(ss_earning_map.get(ss.name, {}).get("Basic"))
		bonus_provision = ((basic*(bonus_rate/100))*bonus_days/total_days)

		leave_points = 0	
		if int(monthly_present[0].present_count) > 18:
			leave_points = 1.33
			leave_reimbursement_provision = (flt(ssa_gross) * 1.33) / 30
			
		row.append(int(bonus_provision))
		row.append(int(Leave))
		row.append(flt(leave_points))
		row.append(int(leave_reimbursement_provision))
	# -------------------------Custom Logic for 3 component--------------------
		for d in ded_types:
			row.append((ss_ded_map.get(ss.name, {}).get(d)))

		row.append(int(ss.total_loan_repayment))

		if currency == company_currency:
			row += [(flt(ss.total_deduction) * flt(ss.exchange_rate)),(flt(ss.net_pay) * flt(ss.exchange_rate))]
		else:
			row += [(ss.total_deduction), (ss.net_pay)]
		row.append(currency or company_currency)
		data.append(row)
	# -------------------------Custom Logic for 3 component-------------------- 
	#Interloop
	# Key function
	if filters.summerize_view == 1:
		an_iterator = itertools.groupby(data, lambda x : x[1])
		data1 = []
		for key, group in an_iterator:
			#bcuz the data vanishes after first use
			store_data = list(group)
			row1 = []
			i = 0
			while i <= 9:
				row1.append(store_data[0][i])
				i = i + 1

			j = 10
			num_len = (len(store_data[0]) - 2)
			while j <= num_len:
				addition = 0
				for item in store_data:
					addition = item[j] + addition
				
				j = j + 1
				
				row1.append(addition)

			data1.append(row1)

		return columns, data1
	else:
		return columns, data
# -------------------------Custom Logic for 3 component--------------------
def get_columns(salary_slips):
	"""
	columns = [
		_("Salary Slip ID") + ":Link/Salary Slip:150",
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::140",
		_("Date of Joining") + "::80",
		_("Branch") + ":Link/Branch:120",
		_("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120",
		_("Company") + ":Link/Company:120",
		_("Start Date") + "::80",
		_("End Date") + "::80",
		_("Leave Without Pay") + ":Float:130",
		_("Payment Days") + ":Float:120",
		_("Currency") + ":Link/Currency:80"
	]
	"""
	columns = [
		_("Salary Slip ID") + ":Link/Salary Slip:150",_("Employee") + ":Link/Employee:120", _("Employee Name") + "::140",
		_("Date of Joining") + "::80", _("Branch") + ":Link/Branch:-1", _("Department") + ":Link/Department:-1",
		_("Designation") + ":Link/Designation:120", _("Company") + ":Link/Company:120", _("Start Date") + "::80",
		_("End Date") + "::80", _("Leave Without Pay") + ":Integer:50", _("Payment Days") + ":Integer:120"
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Integer:120") for e in salary_components[_("Earning")]] + \
		[_("Gross Pay") + ":Integer:120", _("Bonus Provision") + ":Integer:120", _("Leave") + ":Integer:70",_("Leave Points")+":Integer:120",_("Leave Reimbursement Provision") + ":Integer:120"] + [(d + ":Integer:120") for d in salary_components[_("Deduction")]] + \
		[_("Loan Repayment") + ":Integer:120", _("Total Deduction") + ":Integer:120", _("Net Pay") + ":Integer:120"]

	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee""" % conditions, filters, as_dict=1)

	return salary_slips or []

def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"

	return conditions, filters

def get_employee_doj_map():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					date_of_joining
				FROM `tabEmployee`
				"""))

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency):
	ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_ded_map


def get_leave_and_bonus(emp, start_date, end_date,absent_days):

	monthly_present = get_monthly_present(emp,start_date,end_date)
	
	total_days = date_diff(end_date, start_date)+1
	bonus_days = int(total_days-absent_days)
	monthly_present = sorted(monthly_present, key=lambda k: datetime.strptime(k['month'], "%m-%Y"))

	salaryDetails = get_salary_details(emp)

	ssa_gross,basic_salary = get_gross_and_basic_salary(salaryDetails)

	return monthly_present,total_days,bonus_days,ssa_gross

def get_monthly_present(emp,start_date,end_date):

	monthly_present = frappe.db.sql("""select DATE_FORMAT(attendance_date,'%m-%Y') as month,
	count(case when status ='Present'  then 1 end) as present_count,
	count(case when status ='Absent' then 1 end) as absent_count from `tabAttendance` 
	where attendance_date between '{start_date}' and '{end_date}'
	and (status = 'Present' or status = 'Absent') and  employee = '{emp}' group by DATE_FORMAT(attendance_date,'%m-%Y')
	""".format(start_date=start_date,end_date=end_date,emp=emp),as_dict=True)
	return monthly_present

def get_salary_details(emp):
	ssa = frappe.get_last_doc('Salary Structure Assignment', filters={"employee": emp})					
	salaryDetails = frappe.db.sql("""
	select
	sd.salary_component,
	sd.amount
	from
	`tabSalary Detail` sd
	where sd.parent = %s
	and
	sd.parentfield = "earnings"
	""", (ssa.salary_structure),as_dict=True)
	return salaryDetails

def get_gross_and_basic_salary(salaryDetails):
	gross = 0
	for row in salaryDetails:
		gross += row.amount

	basic_salary = salaryDetails[-1].amount
	return gross,basic_salary

