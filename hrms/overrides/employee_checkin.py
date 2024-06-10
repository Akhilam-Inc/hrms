import frappe

def after_insert(self,method):
    if self.shift:
        frappe.db.set_value("Shift Type",self.shift,"last_sync_of_checkin",frappe.utils.now())