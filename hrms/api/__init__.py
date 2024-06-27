import frappe
from frappe import _
from frappe.model.workflow import get_workflow_name
from frappe.query_builder import Order
from frappe.utils import getdate
import requests
from erpnext.accounts.party import get_party_details
from frappe.utils import add_days, flt, getdate, today


SUPPORTED_FIELD_TYPES = [
	"Link",
	"Select",
	"Small Text",
	"Text",
	"Long Text",
	"Text Editor",
	"Table",
	"Check",
	"Data",
	"Float",
	"Int",
	"Section Break",
	"Date",
	"Time",
	"Datetime",
	"Currency",
]


@frappe.whitelist()
def get_current_user_info() -> dict:
	current_user = frappe.session.user
	user = frappe.db.get_value(
		"User", current_user, ["name", "first_name", "full_name", "user_image"], as_dict=True
	)
	user["roles"] = frappe.get_roles(current_user)

	return user


@frappe.whitelist()
def get_current_employee_info() -> dict:
	current_user = frappe.session.user
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": current_user, "status": "Active"},
		[
			"name",
			"first_name",
			"employee_name",
			"designation",
			"department",
			"company",
			"reports_to",
			"user_id",
		],
		as_dict=True,
	)
	return employee


@frappe.whitelist()
def get_all_employees() -> list[dict]:
	return frappe.get_all(
		"Employee",
		fields=[
			"name",
			"employee_name",
			"designation",
			"department",
			"company",
			"reports_to",
			"user_id",
			"image",
			"status",
		],
		limit=999999,
	)


# Notifications
@frappe.whitelist()
def get_unread_notifications_count() -> int:
	return frappe.db.count(
		"PWA Notification",
		{"to_user": frappe.session.user, "read": 0},
	)


@frappe.whitelist()
def mark_all_notifications_as_read() -> None:
	frappe.db.set_value(
		"PWA Notification",
		{"to_user": frappe.session.user, "read": 0},
		"read",
		1,
		update_modified=False,
	)


@frappe.whitelist()
def are_push_notifications_enabled() -> bool:
	try:
		return frappe.db.get_single_value("Push Notification Settings", "enable_push_notification_relay")
	except frappe.DoesNotExistError:
		# push notifications are not supported in the current framework version
		return False


# Leaves and Holidays
@frappe.whitelist()
def get_leave_applications(
	employee: str,
	approver_id: str = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = get_leave_application_filters(employee, approver_id, for_approval)
	fields = [
		"name",
		"employee",
		"employee_name",
		"leave_type",
		"status",
		"from_date",
		"to_date",
		"half_day",
		"half_day_date",
		"description",
		"total_leave_days",
		"leave_balance",
		"leave_approver",
		"posting_date",
	]

	if workflow_state_field := get_workflow_state_field("Leave Application"):
		fields.append(workflow_state_field)

	applications = frappe.get_list(
		"Leave Application",
		fields=fields,
		filters=filters,
		order_by="posting_date desc",
		limit=limit,
	)

	if workflow_state_field:
		for application in applications:
			application["workflow_state_field"] = workflow_state_field

	return applications


def get_leave_application_filters(
	employee: str,
	approver_id: str = None,
	for_approval: bool = False,
) -> dict:
	filters = frappe._dict()
	if for_approval:
		filters.docstatus = 0
		filters.employee = ("!=", employee)

		if workflow := get_workflow("Leave Application"):
			allowed_states = get_allowed_states_for_workflow(workflow, approver_id)
			filters[workflow.workflow_state_field] = ("in", allowed_states)
		else:
			filters.status = "Open"
			filters.leave_approver = approver_id
	else:
		filters.docstatus = ("!=", 2)
		filters.employee = employee

	return filters


@frappe.whitelist()
def get_leave_balance_map(employee: str) -> dict[str, dict[str, float]]:
	"""
	Returns a map of leave type and balance details like:
	{
	        'Casual Leave': {'allocated_leaves': 10.0, 'balance_leaves': 5.0},
	        'Earned Leave': {'allocated_leaves': 3.0, 'balance_leaves': 3.0},
	}
	"""
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	date = getdate()
	leave_map = {}

	leave_details = get_leave_details(employee, date)
	allocation = leave_details["leave_allocation"]

	for leave_type, details in allocation.items():
		leave_map[leave_type] = {
			"allocated_leaves": details.get("total_leaves"),
			"balance_leaves": details.get("remaining_leaves"),
		}

	return leave_map


@frappe.whitelist()
def get_holidays_for_employee(employee: str) -> list[dict]:
	from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

	holiday_list = get_holiday_list_for_employee(employee, raise_exception=False)
	if not holiday_list:
		return []

	Holiday = frappe.qb.DocType("Holiday")
	return (
		frappe.qb.from_(Holiday)
		.select(Holiday.name, Holiday.holiday_date, Holiday.description)
		.where((Holiday.parent == holiday_list) & (Holiday.weekly_off == 0))
		.orderby(Holiday.holiday_date, order=Order.asc)
	).run(as_dict=True)


@frappe.whitelist()
def get_leave_approval_details(employee: str) -> dict:
	leave_approver, department = frappe.get_cached_value(
		"Employee",
		employee,
		["leave_approver", "department"],
	)

	if not leave_approver and department:
		leave_approver = frappe.db.get_value(
			"Department Approver",
			{"parent": department, "parentfield": "leave_approvers", "idx": 1},
			"approver",
		)

	leave_approver_name = frappe.db.get_value("User", leave_approver, "full_name", cache=True)
	department_approvers = get_department_approvers(department, "leave_approvers")

	if leave_approver and leave_approver not in [approver.name for approver in department_approvers]:
		department_approvers.append({"name": leave_approver, "full_name": leave_approver_name})

	return dict(
		leave_approver=leave_approver,
		leave_approver_name=leave_approver_name,
		department_approvers=department_approvers,
		is_mandatory=frappe.db.get_single_value(
			"HR Settings", "leave_approver_mandatory_in_leave_application"
		),
	)


def get_department_approvers(department: str, parentfield: str) -> list[str]:
	if not department:
		return []

	department_details = frappe.db.get_value("Department", department, ["lft", "rgt"], as_dict=True)
	departments = frappe.get_all(
		"Department",
		filters={
			"lft": ("<=", department_details.lft),
			"rgt": (">=", department_details.rgt),
			"disabled": 0,
		},
		pluck="name",
	)

	Approver = frappe.qb.DocType("Department Approver")
	User = frappe.qb.DocType("User")
	department_approvers = (
		frappe.qb.from_(User)
		.join(Approver)
		.on(Approver.approver == User.name)
		.select(User.name.as_("name"), User.full_name.as_("full_name"))
		.where((Approver.parent.isin(departments)) & (Approver.parentfield == parentfield))
	).run(as_dict=True)

	return department_approvers


@frappe.whitelist()
def get_leave_types(employee: str, date: str) -> list:
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	date = date or getdate()

	leave_details = get_leave_details(employee, date)
	leave_types = list(leave_details["leave_allocation"].keys()) + leave_details["lwps"]

	return leave_types


# Expense Claims
@frappe.whitelist()
def get_expense_claims(
	employee: str,
	approver_id: str = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = get_expense_claim_filters(employee, approver_id, for_approval)
	fields = [
		"`tabExpense Claim`.name",
		"`tabExpense Claim`.employee",
		"`tabExpense Claim`.employee_name",
		"`tabExpense Claim`.approval_status",
		"`tabExpense Claim`.status",
		"`tabExpense Claim`.expense_approver",
		"`tabExpense Claim`.total_claimed_amount",
		"`tabExpense Claim`.posting_date",
		"`tabExpense Claim`.company",
		"`tabExpense Claim Detail`.expense_type",
		"count(`tabExpense Claim Detail`.expense_type) as total_expenses",
	]

	if workflow_state_field := get_workflow_state_field("Expense Claim"):
		fields.append(workflow_state_field)

	claims = frappe.get_list(
		"Expense Claim",
		fields=fields,
		filters=filters,
		order_by="`tabExpense Claim`.posting_date desc",
		group_by="`tabExpense Claim`.name",
		limit=limit,
	)

	if workflow_state_field:
		for claim in claims:
			claim["workflow_state_field"] = workflow_state_field

	return claims

@frappe.whitelist()
def get_tv_requests(
	employee: str,
	approver_id: str = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = {"approver": approver_id, "status": "Open"}
	fields = [
		"`tabRequest Form`.name",
		"`tabRequest Form`.employee",
		"`tabRequest Form`.employee_name",
		
		"`tabRequest Form`.status",
		
		"`tabRequest Form`.from_date",
		"`tabRequest Form`.to_date",
		"`tabRequest Form`.half_day",
		"`tabRequest Form`.half_day_date",
		"`tabRequest Form`.reason",
		"`tabRequest Form`.explanation",
		
	]

	if workflow_state_field := get_workflow_state_field("Request Form"):
		fields.append(workflow_state_field)

	tc_requests = frappe.get_all(
		"Request Form",
		fields=fields,
		filters=filters,
		order_by="`tabRequest Form`.creation desc",
		limit=limit,
	)

	if workflow_state_field:
		for claim in tc_requests:
			claim["workflow_state_field"] = workflow_state_field

	return tc_requests


def get_expense_claim_filters(
	employee: str,
	approver_id: str = None,
	for_approval: bool = False,
) -> dict:
	filters = frappe._dict()

	if for_approval:
		filters.docstatus = 0
		filters.employee = ("!=", employee)

		if workflow := get_workflow("Expense Claim"):
			allowed_states = get_allowed_states_for_workflow(workflow, approver_id)
			filters[workflow.workflow_state_field] = ("in", allowed_states)
		else:
			filters.status = "Draft"
			filters.expense_approver = approver_id
	else:
		filters.docstatus = ("!=", 2)
		filters.employee = employee

	return filters


@frappe.whitelist()
def get_expense_claim_summary(employee: str) -> dict:
	from frappe.query_builder.functions import Sum

	Claim = frappe.qb.DocType("Expense Claim")

	pending_claims_case = (
		frappe.qb.terms.Case()
		.when(Claim.approval_status == "Draft", Claim.total_claimed_amount)
		.else_(0)
	)
	sum_pending_claims = Sum(pending_claims_case).as_("total_pending_amount")

	approved_claims_case = (
		frappe.qb.terms.Case()
		.when(Claim.approval_status == "Approved", Claim.total_sanctioned_amount)
		.else_(0)
	)
	sum_approved_claims = Sum(approved_claims_case).as_("total_approved_amount")

	rejected_claims_case = (
		frappe.qb.terms.Case()
		.when(Claim.approval_status == "Rejected", Claim.total_sanctioned_amount)
		.else_(0)
	)
	sum_rejected_claims = Sum(rejected_claims_case).as_("total_rejected_amount")

	summary = (
		frappe.qb.from_(Claim)
		.select(
			sum_pending_claims,
			sum_approved_claims,
			sum_rejected_claims,
			Claim.company,
		)
		.where((Claim.docstatus != 2) & (Claim.employee == employee))
	).run(as_dict=True)[0]

	currency = frappe.db.get_value("Company", summary.company, "default_currency")
	summary["currency"] = currency

	return summary


@frappe.whitelist()
def get_expense_type_description(expense_type: str) -> str:
	return frappe.db.get_value("Expense Claim Type", expense_type, "description")


@frappe.whitelist()
def get_expense_claim_types() -> list[dict]:
	ClaimType = frappe.qb.DocType("Expense Claim Type")

	return (frappe.qb.from_(ClaimType).select(ClaimType.name, ClaimType.description)).run(
		as_dict=True
	)


@frappe.whitelist()
def get_expense_approval_details(employee: str) -> dict:
	expense_approver, department = frappe.get_cached_value(
		"Employee",
		employee,
		["expense_approver", "department"],
	)

	if not expense_approver and department:
		expense_approver = frappe.db.get_value(
			"Department Approver",
			{"parent": department, "parentfield": "expense_approvers", "idx": 1},
			"approver",
		)

	expense_approver_name = frappe.db.get_value("User", expense_approver, "full_name", cache=True)
	department_approvers = get_department_approvers(department, "expense_approvers")

	if expense_approver and expense_approver not in [
		approver.name for approver in department_approvers
	]:
		department_approvers.append({"name": expense_approver, "full_name": expense_approver_name})

	return dict(
		expense_approver=expense_approver,
		expense_approver_name=expense_approver_name,
		department_approvers=department_approvers,
		is_mandatory=frappe.db.get_single_value(
			"HR Settings", "expense_approver_mandatory_in_expense_claim"
		),
	)


# Employee Advance
@frappe.whitelist()
def get_employee_advance_balance(employee: str) -> list[dict]:
	Advance = frappe.qb.DocType("Employee Advance")

	advances = (
		frappe.qb.from_(Advance)
		.select(
			Advance.name,
			Advance.employee,
			Advance.status,
			Advance.purpose,
			Advance.paid_amount,
			(Advance.paid_amount - (Advance.claimed_amount + Advance.return_amount)).as_("balance_amount"),
			Advance.posting_date,
			Advance.currency,
		)
		.where(
			(Advance.docstatus == 1)
			& (Advance.paid_amount)
			& (Advance.employee == employee)
			# don't need claimed & returned advances, only partly or completely paid ones
			& (Advance.status.isin(["Paid", "Unpaid"]))
		)
		.orderby(Advance.posting_date, order=Order.desc)
	).run(as_dict=True)

	return advances


@frappe.whitelist()
def get_advance_account(company: str) -> str | None:
	return frappe.db.get_value("Company", company, "default_employee_advance_account", cache=True)


# Company
@frappe.whitelist()
def get_company_currencies() -> dict:
	Company = frappe.qb.DocType("Company")
	Currency = frappe.qb.DocType("Currency")

	query = (
		frappe.qb.from_(Company)
		.join(Currency)
		.on(Company.default_currency == Currency.name)
		.select(
			Company.name,
			Company.default_currency,
			Currency.name.as_("currency"),
			Currency.symbol.as_("symbol"),
		)
	)

	companies = query.run(as_dict=True)
	return {company.name: (company.default_currency, company.symbol) for company in companies}


@frappe.whitelist()
def get_currency_symbols() -> dict:
	Currency = frappe.qb.DocType("Currency")

	currencies = (frappe.qb.from_(Currency).select(Currency.name, Currency.symbol)).run(as_dict=True)

	return {currency.name: currency.symbol or currency.name for currency in currencies}


@frappe.whitelist()
def get_company_cost_center_and_expense_account(company: str) -> dict:
	return frappe.db.get_value(
		"Company", company, ["cost_center", "default_expense_claim_payable_account"], as_dict=True
	)


# Form View APIs
@frappe.whitelist()
def get_doctype_fields(doctype: str) -> list[dict]:
	fields = frappe.get_meta(doctype).fields
	return [
		field
		for field in fields
		if field.fieldtype in SUPPORTED_FIELD_TYPES and field.fieldname != "amended_from"
	]


@frappe.whitelist()
def get_doctype_states(doctype: str) -> dict:
	states = frappe.get_meta(doctype).states
	return {state.title: state.color.lower() for state in states}


# File
@frappe.whitelist()
def get_attachments(dt: str, dn: str):
	from frappe.desk.form.load import get_attachments

	return get_attachments(dt, dn)


@frappe.whitelist()
def upload_base64_file(content, filename, dt=None, dn=None, fieldname=None):
	import base64
	import io
	from mimetypes import guess_type

	from PIL import Image, ImageOps

	from frappe.handler import ALLOWED_MIMETYPES

	decoded_content = base64.b64decode(content)
	content_type = guess_type(filename)[0]
	if content_type not in ALLOWED_MIMETYPES:
		frappe.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

	if content_type.startswith("image/jpeg"):
		# transpose the image according to the orientation tag, and remove the orientation data
		with Image.open(io.BytesIO(decoded_content)) as image:
			transpose_img = ImageOps.exif_transpose(image)
			# convert the image back to bytes
			file_content = io.BytesIO()
			transpose_img.save(file_content, format="JPEG")
			file_content = file_content.getvalue()
	else:
		file_content = decoded_content

	return frappe.get_doc(
		{
			"doctype": "File",
			"attached_to_doctype": dt,
			"attached_to_name": dn,
			"attached_to_field": fieldname,
			"folder": "Home",
			"file_name": filename,
			"content": file_content,
			"is_private": 1,
		}
	).insert()


@frappe.whitelist()
def delete_attachment(filename: str):
	frappe.delete_doc("File", filename)


@frappe.whitelist()
def download_salary_slip(name: str):
	import base64

	from frappe.utils.print_format import download_pdf

	default_print_format = frappe.get_meta("Salary Slip").default_print_format or "Standard"

	try:
		download_pdf("Salary Slip", name, format=default_print_format)
	except Exception:
		frappe.throw(_("Failed to download Salary Slip PDF"))

	base64content = base64.b64encode(frappe.local.response.filecontent)
	content_type = frappe.local.response.type

	return f"data:{content_type};base64," + base64content.decode("utf-8")


# Workflow
@frappe.whitelist()
def get_workflow(doctype: str) -> dict:
	workflow = get_workflow_name(doctype)
	if not workflow:
		return frappe._dict()
	return frappe.get_doc("Workflow", workflow)


def get_workflow_state_field(doctype: str) -> str | None:
	workflow_name = get_workflow_name(doctype)
	if not workflow_name:
		return None

	override_status, workflow_state_field = frappe.db.get_value(
		"Workflow",
		workflow_name,
		["override_status", "workflow_state_field"],
	)
	# NOTE: checkbox labelled 'Don't Override Status' is named override_status hence the inverted logic
	if not override_status:
		return workflow_state_field
	return None


def get_allowed_states_for_workflow(workflow: dict, user_id: str) -> list[str]:
	user_roles = frappe.get_roles(user_id)
	return [
		transition.state for transition in workflow.transitions if transition.allowed in user_roles
	]




@frappe.whitelist()
def upload_file(file_list, dt=None, dn=None):
	for row in file_list:
		upload_base64_file(file_list[row], row, dt , dn)


def get_location_for_lat_lng(lat, lng):
	"""
	The function `get_location_for_lat_lng` takes latitude and longitude coordinates as input and
	returns the location information for that coordinates using a reverse geocoding API.

	:param lat: The `lat` parameter represents the latitude coordinate of a location
	:param lng: The `lng` parameter represents the longitude coordinate of a location
	:return: a JSON response containing location information for the given latitude and longitude
	coordinates.
	"""
	url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
	response = requests.request("GET", url, headers={}, data={})
	if response.ok:
		response=response.json()
		response.pop('licence')
		response.pop('osm_type')
		response.pop('osm_id')
		return response
	else:
		frappe.log_error("get_location_for_lat_lng", response.text)

def get_location(lat, lng):
	from geopy.geocoders import Nominatim
	geolocator = Nominatim(user_agent="geo_locator")

	location = f"{lat}, {lng}"
	try:
		address = geolocator.reverse(location)
		return address.address if address else "Location not found"

	except Exception as e:
		frappe.log_error("get_location", frappe.get_traceback())
		return "Location not found"

def record_place_name(self, method):
	try:
		# frappe.msgprint("Record Place Name")
		if self.doctype == "Employee Checkin":
			if self.get("custom_latitude") and self.get("custom_longitude") and not self.custom_place_name:
				self.custom_place_name = get_location(self.get("custom_latitude") , self.get("custom_longitude"))

		if self.doctype == "Field Report":
			if self.get("latitude") and self.get("longitude") and not self.place_name:
				self.place_name = get_location(self.get("latitude") , self.get("longitude"))
	
	except Exception as e:
		frappe.log_error("record_place_name", frappe.get_traceback())





@frappe.whitelist()
def create_sales_order(**args):
	price_list = frappe.db.get_value("Customer",args["customer"],"default_price_list")
	company = frappe.get_single("Global Defaults").default_company
	
	employee_id = frappe.db.get_value("Employee", {"user_id": args["user"]})
	sales_person = frappe.db.get_value("Sales Person", {"employee": employee_id})
	sales_team = []
	if sales_person:
		sales_team = [{"sales_person": sales_person, "allocated_percentage":100}]
	if not price_list:
		frappe.throw(f"Price list is not assigned in customer group of customer {args['customer']}")

	try:
		so = frappe.get_doc({
			'doctype': "Sales Order",
			'transaction_date': args["date"] or today(),
			'company' : company,
			'customer' : args["customer"],
			'delivery_date' : args["delivery_date"],
			'sales_team' : sales_team,
			'price_list'  : price_list,
			'items': args["item"],
			'order_type' : "Sales",
		})
		
		party_details = get_party_details(party=so.customer,party_type='Customer',posting_date=frappe.utils.today(),company=company,doctype='Sales Order')
		so.taxes_and_charges = party_details.get("taxes_and_charges")
		so.set("taxes", party_details.get("taxes"))
		so.set_missing_values()
		so.calculate_taxes_and_totals()
		so.insert(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(title = "Sales Order Creation",message = frappe.get_traceback())


@frappe.whitelist()
def create_customer(**args):
	try:
		args = args["customer"]
		customer_doc = frappe.get_doc({
						"doctype":"Customer",
						"customer_name": args["customer_name"],
						"tax_id": args["custom_gst_number"],
						"account_manager":frappe.session.user,
				}).insert(ignore_permissions=True)

		address_doc = frappe.get_doc(
						{
							"doctype": "Address",
							"address_title": args["customer_name"],
							"address_type": "Billing",
							"address_line1": args["custom_firm_name"],
							"city": args["custom_city"],
							"state": args["custom_city"],
							"links": [{"link_doctype": "Customer", "link_name": customer_doc.name}],
							"gstin": args["custom_gst_number"],
							"email_id": args["custom_email_address"],
							"phone": args["custom_phone"]
				}).insert(ignore_permissions=True)

		contact_doc = frappe.get_doc(
						{
							"doctype": "Contact",
							"first_name": args["customer_name"],
							"company_name": args["custom_firm_name"],
							"address": address_doc.name,
							"email_ids": [{"email_id": args["custom_email_address"], "is_primary": 1}],
							"phone_nos": [{"phone": args["custom_phone"], "is_primary_phone": 1, "is_primary_mobile_no": 1}],
							"links": [{"link_doctype": "Customer", "link_name": customer_doc.name}],
				}).insert(ignore_permissions=True)

		customer_doc.customer_primary_address = address_doc.name
		customer_doc.customer_primary_contact = contact_doc.name
		customer_doc.save(ignore_permissions=True)
	
	except Exception as e:
		frappe.log_error(title = "Customer Creation",message = frappe.get_traceback())

@frappe.whitelist()
def get_customer():
	return frappe.get_all("Customer", {'disabled': 0}, pluck="name")