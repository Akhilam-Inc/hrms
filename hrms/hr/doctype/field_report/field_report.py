# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.api import get_location
from frappe import _

class FieldReport(Document):
	def validate(self):
		try:
			if self.get("custom_latitude") and self.get("custom_longitude") and not self.place_name:
				self.place_name = get_location(self.get("custom_latitude") , self.get("custom_longitude"))

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), _("Field Report Error"))
			frappe.msgprint(_("Not Able to fetch location name. Please check the permission for the location."))
