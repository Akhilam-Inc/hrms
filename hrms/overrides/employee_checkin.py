import frappe
from datetime import datetime

def after_insert(self,method):
    if self.shift:
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        frappe.db.set_value("Shift Type",self.shift,"last_sync_of_checkin",current_datetime)