import frappe

def on_submit(doc,method):
    bpt_doc = frappe.get_doc('Bindal Payroll Tool', doc.bindal_payroll_tool)
    for bpt in bpt_doc.tool_item:
        if bpt.incentive == doc.amount and bpt.employee_name == doc.employee_name:
            frappe.db.set_value('Bindal Payroll Tool Item',{'parent':doc.bindal_payroll_tool,'name':doc.bindal_payroll_child_table_reference},'additional_salary_reference',doc.name)
            
        if bpt.leave_rehembance == doc.amount and bpt.employee_name == doc.employee_name: 
            frappe.db.set_value('Bindal Payroll Tool Item',{'parent':doc.bindal_payroll_tool,'name':doc.bindal_payroll_child_table_reference},'additional_salary_leave_reference',doc.name)
