import frappe

def validate(doc,method):
    pass
    # is_cash = frappe.db.get_value("Employee", doc.employee, "cash_employee_custom")

    # if is_cash:
    #     frappe.throw("Employee: {employee} is a Cash Customer, You cannot create Salary Structure for that employee!".format(employee = doc.employee))