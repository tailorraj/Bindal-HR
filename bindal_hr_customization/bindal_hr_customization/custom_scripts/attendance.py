import frappe

def get_miss_check_in_or_out(self,method):

    if (self.in_time and not self.out_time) or (self.out_time and not self.in_time):
        self.miss_in_out = 1
    else:
        self.miss_in_out = 0

# bindal_hr_customization.bindal_hr_customization.custom_scripts.attendance.get_miss_check_in_or_out