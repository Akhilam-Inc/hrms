# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.api import get_location_for_lat_lng
from frappe import _

class FieldReport(Document):
	def validate(self):
		try:
			self.place_name = get_location_for_lat_lng(self.get("latitude") , self.get("longitude")).get('display_name') or ""
		except Exception as e:
			
			frappe.log_error(frappe.get_traceback(), _("Field Report Error"))
			frappe.msgprint(_("Not Able to fetch location name. Please check the permission for the location."))
