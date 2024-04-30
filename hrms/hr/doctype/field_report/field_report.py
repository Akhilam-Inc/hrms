# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.api import get_location_for_lat_lng


class FieldReport(Document):
	def validate(self):
		self.place_name = get_location_for_lat_lng(self.get("latitude") , self.get("longitude")).get('display_name') or ""
