import frappe
from frappe import _
from frappe.utils import money_in_words
from frappe.utils.csvutils import getlink

import erpnext
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from datetime import date, timedelta, datetime
import json

class Fees(AccountsController):
	def set_indicator(self):
		"""Set indicator for portal"""
		if self.outstanding_amount > 0:
			self.indicator_color = "orange"
			self.indicator_title = _("Unpaid")
		else:
			self.indicator_color = "green"
			self.indicator_title = _("Paid")

	def validate(self):
		self.calculate_total()
		self.set_missing_accounts_and_fields()

	def set_missing_accounts_and_fields(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().company
		if not self.currency:
			self.currency = erpnext.get_company_currency(self.company)
		################################################################	
		if not (self.receivable_account and self.income_account and self.cost_center):
			accounts_details = frappe.get_all("Company",
				fields=["default_receivable_account", "default_income_account", "cost_center"],
				filters={"name": self.company})[0]

		if not self.receivable_account:
			self.receivable_account = accounts_details.default_receivable_account
		if not self.income_account:
			self.income_account = accounts_details.default_income_account
		################################################################	
		if not self.cost_center:
			self.cost_center = accounts_details.cost_center
		if not self.student_email:
			self.student_email = self.get_student_emails()

	def get_student_emails(self):
		student_emails = frappe.db.sql_list("""
			select g.email_address
			from `tabGuardian` g, `tabStudent Guardian` sg
			where g.name = sg.guardian and sg.parent = %s and sg.parenttype = 'Student'
			and ifnull(g.email_address, '')!=''
		""", self.student)

		student_email_id = frappe.db.get_value("Student", self.student, "student_email_id")
		if student_email_id:
			student_emails.append(student_email_id)
		if student_emails:
			return ", ".join(list(set(student_emails)))
		else:
			return None


	def calculate_total(self):
		"""Calculates total amount."""
		self.grand_total = 0
		for d in self.components:
			self.grand_total += d.amount
		self.outstanding_amount = self.grand_total
		self.grand_total_in_words = money_in_words(self.grand_total)

	def on_submit(self):
		self.make_gl_entries()

		if self.send_payment_request and self.student_email:
			pr = make_payment_request(party_type="Student", party=self.student, dt="Fees",
					dn=self.name, recipient_id=self.student_email,
					submit_doc=True, use_dummy_message=True)
			frappe.msgprint(_("Payment request {0} created").format(getlink("Payment Request", pr.name)))
		#############################	
		frappe.db.set_value("Fees", self.name, "outstanding_amount",self.outstanding_amount)
		####################################


	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry', 'Stock Ledger Entry')
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
		# frappe.db.set(self, 'status', 'Cancelled')


	def make_gl_entries(self):
		if not self.grand_total:
			return
		####################################################################	completed
		data = frappe.get_all("Fee Component",{"parent":self.name},["fees_category","receivable_account","income_account","amount"])
		for fc in data:
			student_gl_entries =  self.get_gl_dict({
				"account": fc["receivable_account"],
				"party_type": "Student",
				"party": self.student,
				"against": fc["income_account"],
				"debit": fc["amount"],
				"debit_in_account_currency": fc["amount"],
				"against_voucher": self.name,
				"against_voucher_type": self.doctype
			}, item=self)

			fee_gl_entry = self.get_gl_dict({
				"account": fc["income_account"],
				"against": self.student,
				"credit": fc["amount"],
				"credit_in_account_currency": fc["amount"],
				"cost_center": self.cost_center
			}, item=self)
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries([student_gl_entries, fee_gl_entry], cancel=(self.docstatus == 2),
				update_outstanding="Yes", merge_entries=False)
		###################################################################	

def get_fee_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"):
	user = frappe.session.user
	student = frappe.db.sql("select name from `tabStudent` where student_email_id= %s", user)
	if student:
		return frappe. db.sql('''
			select name, program, due_date, grand_total - outstanding_amount as paid_amount,
			outstanding_amount, grand_total, currency
			from `tabFees`
			where student= %s and docstatus=1
			order by due_date asc limit {0} , {1}'''
			.format(limit_start, limit_page_length), student, as_dict = True)

def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		'no_breadcrumbs': True,
		"title": _("Fees"),
		"get_list": get_fee_list,
		"row_template": "templates/includes/fee/fee_row.html"
	}

@frappe.whitelist()
def make_fees(frm):
    args = json.loads(frm)
    fees = frappe.new_doc("Fees")
    fees.student= args["party"]
    fees.student_name= args["party_name"]
    fees.roll_no= frappe.get_all("Student",{"name":args["party"]},["roll_no"])[0]['roll_no']
    fees.registration_number= frappe.get_all("Student",{"name":args["party"]},["permanant_registration_number"])[0]['permanant_registration_number']
    fees.vidyarthi_portal_id= frappe.get_all("Student",{"name":args["party"]},["vidyarthi_portal_id"])[0]['vidyarthi_portal_id']
    fees.sams_portal_id= frappe.get_all("Student",{"name":args["party"]},["sams_portal_id"])[0]['sams_portal_id']
    fees.student_category= frappe.get_all("Student",{"name":args["party"]},["student_category"])[0]['student_category']
    fees.student_email= frappe.get_all("Student",{"name":args["party"]},["student_email_id"])[0]['student_email_id']
    data=frappe.get_all("Program Enrollment",{'student':args["party"],'docstatus':1},['name','program','programs','student_batch_name','academic_year','academic_term'],
    order_by= "name desc")
    if len(data)>0:
        fees.program_enrollment= data[0]["name"]
        fees.programs= data[0]["programs"]
        fees.program= data[0]["program"]
        fees.student_batch= data[0]["student_batch_name"]
        fees.academic_term= data[0]["academic_term"]
        fees.academic_year= data[0]["academic_year"]
    return fees