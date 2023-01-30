# Copyright (c) 2023, Raaj tailor and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, date_diff
from datetime import datetime
import itertools

import erpnext
from bindal_hr_customization.bindal_hr_customization.doctype.bindal_payroll_tool.bindal_payroll_tool import get_salary_details, get_gross_and_basic_salary, get_monthly_present, get_absent_and_leave_points

def execute(filters=None):
	# test()
	if not filters: filters = {}
	currency = None
	if filters.get('currency'):
		currency = filters.get('currency')
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips: return [], []

	columns, earning_types, ded_types = get_columns(salary_slips)
	

	data = []
	if filters.summerize_view == 1:
		salary_slips_summerize = get_salary_slips_summerize(filters, company_currency)
		salary_slip_to_exec = salary_slips_summerize
		is_summery = 1
	else:
		salary_slip_to_exec = salary_slips
		is_summery = 0

	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency, is_summery)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency, is_summery)
	
	doj_map = get_employee_doj_map()
	for ss in salary_slip_to_exec:
		row = [ss.name, ss.employee, ss.employee_name, doj_map.get(ss.employee), ss.branch, ss.department, ss.designation,
			ss.company, ss.start_date, ss.end_date, ss.leave_without_pay, ss.payment_days]

		if ss.branch is not None: columns[3] = columns[3].replace('-1','120')
		if ss.department is not None: columns[4] = columns[4].replace('-1','120')
		if ss.designation is not None: columns[5] = columns[5].replace('-1','120')
		if ss.leave_without_pay is not None: columns[9] = columns[9].replace('-1','130')


		# frappe.masprint()

		for e in earning_types:
			row.append(ss_earning_map.get(ss.name, {}).get(e))

		if currency == company_currency:
			row += [flt(ss.gross_pay) * flt(ss.exchange_rate)]
		else:
			row += [ss.gross_pay]

		bonus_provision = 0
		leave_reimbursement_provision = 0
		Leave = int(ss.absent_days)

		
		basic = flt(ss_earning_map.get(ss.name, {}).get("Basic"))
		# bonus_provision = ((basic*(8.33/100))* int(ss.payment_days))/(int(ss.total_working_days))
		bonus_provision = ((basic*(8.33/100))* 1)

		if filters.summerize_view == 1:
			monthly_present, gross  = get_leave_and_bonus(ss.employee, filters.from_date, filters.to_date, filters.summerize_view, salary_slips)	
			# total_leave_point = 0
			# for item in monthly_present:
			# 	if int(item.present_count) > 18:
			# 		total_leave_point = total_leave_point + 1.33

			leave_reimbursement_provision = (flt(gross) * 1.33) / 100
		else:
			monthly_present = get_leave_and_bonus(ss.employee, ss.start_date, ss.end_date, filters.summerize_view)	
			if int(monthly_present[0].present_count) > 18:
				leave_reimbursement_provision = (flt(ss.gross_pay) * 1.33) / 100
			
			# frappe.msgprint(str(monthly_present))
		
		
		# Leave = monthly_present[0].absent_count
		row.append(bonus_provision)
		row.append(Leave)
		row.append(leave_reimbursement_provision) 

		for d in ded_types:
			row.append(ss_ded_map.get(ss.name, {}).get(d))

		row.append(ss.total_loan_repayment)

		if currency == company_currency:
			row += [flt(ss.total_deduction) * flt(ss.exchange_rate), flt(ss.net_pay) * flt(ss.exchange_rate)]
		else:
			row += [ss.total_deduction, ss.net_pay]
		row.append(currency or company_currency)
	

		data.append(row)

	#Interloop
	# Key function
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
		while j <= 26:
			addition = 0
			for item in store_data:
				addition += item[j]
			
			j = j + 1
				
			row1.append(addition)
		
		frappe.msgprint(str(row1))

		data1.append(row1)

	return columns, data1

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
		_("End Date") + "::80", _("Leave Without Pay") + ":Float:50", _("Payment Days") + ":Float:120"
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Currency:120") for e in salary_components[_("Earning")]] + \
		[_("Gross Pay") + ":Currency:120", _("Bonus Provision") + ":Currency:120", _("Leave") + ":Integer:120",_("Leave Reimbursement Provision") + ":Currency:120"] + [(d + ":Currency:120") for d in salary_components[_("Deduction")]] + \
		[_("Loan Repayment") + ":Currency:120", _("Total Deduction") + ":Currency:120", _("Net Pay") + ":Currency:120"]

	# columns = columns + [_("Bonus Provision") + ":Currency:120"] + [_("Leave Reimbursement Provision") + ":Currency:120"]
	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)

	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee""" % conditions, filters, as_dict=1)

	return salary_slips or []

def get_salary_slips_summerize(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)

	salary_slips = frappe.db.sql("""select 
	name,
	employee,
	employee_name,
	branch,
	department,
	designation,
	company,
	start_date,
	end_date,
	sum(leave_without_pay) as leave_without_pay,
	sum(payment_days) as payment_days,
	sum(gross_pay) as gross_pay,
	exchange_rate,
	sum(absent_days) as absent_days,
	sum(total_working_days) as total_working_days,
	sum(total_loan_repayment) as total_loan_repayment,
	sum(total_deduction) as total_deduction,
	sum(net_pay) as net_pay
	from `tabSalary Slip` where %s
	group by employee	
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

def get_ss_earning_map(salary_slips, currency, company_currency, is_summery):
	if is_summery == 0:
	# original Code
		ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
			from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
			(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)
	else:
		ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sum(sd.amount) as amount, ss.exchange_rate, ss.name
			from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)
			group by ss.employee, sd.salary_component
			order by ss.employee
			""" %
			(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency, is_summery):
	if is_summery == 0:
	# original Code
		ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
			from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
			(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)
	else:
		ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sum(sd.amount) as amount, ss.exchange_rate, ss.name
			from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)
			group by ss.employee, sd.salary_component
			order by ss.employee
			""" %
			(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_ded_map

def get_leave_and_bonus(emp, start_date, end_date, is_summery,salary_slips=None):

	monthly_present = get_monthly_present(emp,start_date,end_date)
	monthly_present = sorted(monthly_present, key=lambda k: datetime.strptime(k['month'], "%m-%Y"))
	# frappe.msgprint(str(monthly_present[0].month))
	if is_summery == 1:
		gross = 0
		for item in salary_slips:
			for i in monthly_present:
				if item.start_date.year == datetime.strptime(i.month, "%m-%Y").year:
					if item.start_date.month == datetime.strptime(i.month, "%m-%Y").month:
						if i.present_count > 17:
							gross = gross + item.gross_pay
							continue	
	
		return monthly_present, gross
	else:
		return monthly_present


def test():
	L = [("a", 1), ("a", 2), ("b", 3), ("b", 4)]
	# Key function
	an_iterator = itertools.groupby(L, lambda x : x[0])

	for key, group in an_iterator:
		addition = 0
		for item in list(group):
			addition += item[1]
			# frappe.msgprint(str(item[1]))
		
		# frappe.msgprint(str(addition))
		key_and_group = {key : addition}
		frappe.msgprint(str(key_and_group))
