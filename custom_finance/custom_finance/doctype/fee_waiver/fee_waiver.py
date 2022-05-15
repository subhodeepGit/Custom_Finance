# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from six import iteritems, string_types
import json
from frappe.utils import cint, cstr, flt, formatdate, getdate, now
from erpnext.accounts.doctype.budget.budget import validate_expense_against_budget
from frappe.utils import money_in_words
import erpnext


class ClosedAccountingPeriod(frappe.ValidationError): pass

class FeeWaiver(Document):

	def validate(self):
		self.calculate_total()
		self.set_missing_accounts_and_fields()


	def on_submit(self):
		gl_cancelation(self)
		self.make_gl_entries()


	def calculate_total(self):
		"""Calculates total amount."""
		self.grand_total = 0
		self.outstanding_amount=0
		for d in self.fee_componemts:
			self.grand_total += d.waiver_amount
			self.outstanding_amount =self.outstanding_amount+int(d.outstanding_fees)
		self.grand_total_in_words = money_in_words(self.grand_total)

	def set_missing_accounts_and_fields(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().company
		if not self.currency:
			self.currency = erpnext.get_company_currency(self.company)
		if not self.cost_center:
			accounts_details = frappe.get_all("Company",
				fields=["default_receivable_account", "default_income_account", "cost_center"],
				filters={"name": self.company})[0]
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
	def make_gl_entries(self):
		if not self.grand_total:
			return
				####################################################################	completed
		data = frappe.get_all("Fee Component",{"parent":self.name},["fees_category","receivable_account","income_account","amount"])
		for fc in data:
			# student_gl_entries =  self.get_gl_dict({
			# 	"account": fc["receivable_account"],
			# 	"party_type": "Student",
			# 	"party": self.student,
			# 	"against": fc["income_account"],
			# 	"debit": fc["amount"],
			# 	"debit_in_account_currency": fc["amount"],
			# 	"against_voucher": self.name,
			# 	"against_voucher_type": self.doctype
			# }, item=self)

			# fee_gl_entry = self.get_gl_dict({
			# 	"account": fc["income_account"],
			# 	"against": self.student,
			# 	"credit": fc["amount"],
			# 	"credit_in_account_currency": fc["amount"],
			# 	"cost_center": self.cost_center
			# }, item=self)
			student_gl_entries={'company': 'KiiT Polytechnic', 'posting_date': '2022-05-14', 'fiscal_year': '2022-2023', 'voucher_type': 'Fees', 'voucher_no': 'EDU-FEE-2022-00076', 
			'remarks': None, 'debit': 5800.0, 'credit': 0, 'debit_in_account_currency': 5800.0, 'credit_in_account_currency': 0, 'is_opening': 'No', 'party_type': 'Student', 
			'party': 'EDU-STU-2022-00001', 'project': None, 'post_net_value': None, 'account': 'Development Fees - KP', 'against': 'Development Fees Income - KP', 
			'against_voucher': 'EDU-FEE-2022-00076', 'against_voucher_type': 'Fees', 'account_currency': 'INR'} # This gl will be 2 enrty
			fee_gl_entry={'company': 'KiiT Polytechnic', 'posting_date': '2022-05-14', 'fiscal_year': '2022-2023', 'voucher_type': 'Fees', 
			'voucher_no': 'EDU-FEE-2022-00076', 'remarks': None, 'debit': 0, 'credit': 5800.0, 'debit_in_account_currency': 0, 'credit_in_account_currency': 5800.0, 
			'is_opening': 'No', 'party_type': None, 'party': None, 'project': None, 'post_net_value': None, 'account': 'Development Fees Income - KP', 
			'against': 'EDU-STU-2022-00001', 'cost_center': 'Main - KP', 'account_currency': 'INR'} # one entry 
			print(student_gl_entries)
			print(fee_gl_entry)
			# from erpnext.accounts.general_ledger import make_gl_entries
			# make_gl_entries([student_gl_entries, fee_gl_entry], cancel=(self.docstatus == 2), code has to be copied 
			# 	update_outstanding="Yes", merge_entries=False)
		###################################################################




def gl_cancelation(self):
	GL_account_info=[]
	for t in self.get("fee_componemts"):
		Gl_entry=frappe.db.get_all("GL Entry",filters=[["voucher_no","=",t.fee_voucher_no],["account","=",t.receivable_account]],fields=['name', 'creation', 'modified', 'modified_by', 'owner', 
		'docstatus', 'parent', 'parentfield', 'parenttype', 'idx', 'posting_date', 'transaction_date', 'account', 'party_type', 'party', 'cost_center', 'debit', 'credit', 'account_currency', 
		'debit_in_account_currency', 'credit_in_account_currency', 'against', 'against_voucher_type', 'against_voucher', 'voucher_type', 'voucher_no', 'voucher_detail_no', 'project', 'remarks', 
		'is_opening', 'is_advance','fiscal_year', 'company', 'finance_book', 'to_rename', 'due_date', 'is_cancelled', '_user_tags', '_comments', '_assign', '_liked_by'])
		GL_account_info.append(Gl_entry[0])
		Gl_entry=frappe.db.get_all("GL Entry",filters=[["voucher_no","=",t.fee_voucher_no],["account","=",t.income_account]],fields=['name', 'creation', 'modified', 'modified_by', 
		'owner', 'docstatus', 'parent', 'parentfield', 'parenttype', 'idx', 'posting_date', 'transaction_date', 'account', 'party_type', 'party', 'cost_center', 'debit', 'credit', 
		'account_currency', 'debit_in_account_currency', 'credit_in_account_currency', 'against', 'against_voucher_type', 'against_voucher', 'voucher_type', 'voucher_no', 'voucher_detail_no', 
		'project', 'remarks', 'is_opening', 'is_advance', 'fiscal_year', 'company', 'finance_book', 'to_rename', 'due_date', 'is_cancelled', '_user_tags', '_comments', '_assign', '_liked_by'])
		GL_account_info.append(Gl_entry[0])
	gl_entries=GL_account_info
	make_reverse_gl_entries(gl_entries=gl_entries,voucher_type='Fees')

def make_reverse_gl_entries(gl_entries=None, voucher_type=None, voucher_no=None,adv_adj=False, update_outstanding="Yes"):
	"""
		Get original gl entries of the voucher
		and make reverse gl entries by swapping debit and credit
	"""
	if gl_entries:
		validate_accounting_period(gl_entries)
		check_freezing_date(gl_entries[0]["posting_date"], adv_adj)
		gl_name=[]
		for t in gl_entries:
			gl_name.append(t['name'])	
		set_as_cancel(gl_entries[0]['voucher_type'], gl_entries[0]['voucher_no'],gl_name)
		for entry in gl_entries:
			entry['name'] = None
			debit = entry.get('debit', 0)
			credit = entry.get('credit', 0)
			debit_in_account_currency = entry.get('debit_in_account_currency', 0)
			credit_in_account_currency = entry.get('credit_in_account_currency', 0)

			entry['debit'] = credit
			entry['credit'] = debit
			entry['debit_in_account_currency'] = credit_in_account_currency
			entry['credit_in_account_currency'] = debit_in_account_currency

			entry['remarks'] = "On cancellation of " + entry['voucher_no']
			entry['is_cancelled'] = 1

			if entry['debit'] or entry['credit']:
				make_entry(entry, adv_adj, "Yes")

def validate_accounting_period(gl_map):
	accounting_periods = frappe.db.sql(""" SELECT
			ap.name as name
		FROM
			`tabAccounting Period` ap, `tabClosed Document` cd
		WHERE
			ap.name = cd.parent
			AND ap.company = %(company)s
			AND cd.closed = 1
			AND cd.document_type = %(voucher_type)s
			AND %(date)s between ap.start_date and ap.end_date
			""", {
				'date': gl_map[0].posting_date,
				'company': gl_map[0].company,
				'voucher_type': gl_map[0].voucher_type
			}, as_dict=1)

	if accounting_periods:
		frappe.throw(_("You cannot create or cancel any accounting entries with in the closed Accounting Period {0}")
			.format(frappe.bold(accounting_periods[0].name)), ClosedAccountingPeriod)

def check_freezing_date(posting_date, adv_adj=False):
	"""
		Nobody can do GL Entries where posting date is before freezing date
		except authorized person

		Administrator has all the roles so this check will be bypassed if any role is allowed to post
		Hence stop admin to bypass if accounts are freezed
	"""
	if not adv_adj:
		acc_frozen_upto = frappe.db.get_value('Accounts Settings', None, 'acc_frozen_upto')
		if acc_frozen_upto:
			frozen_accounts_modifier = frappe.db.get_value( 'Accounts Settings', None,'frozen_accounts_modifier')
			if getdate(posting_date) <= getdate(acc_frozen_upto) \
					and (frozen_accounts_modifier not in frappe.get_roles() or frappe.session.user == 'Administrator'):
				frappe.throw(_("You are not authorized to add or update entries before {0}").format(formatdate(acc_frozen_upto)))


def set_as_cancel(voucher_type, voucher_no,gl_name):
	"""
		Set is_cancelled=1 for perticular gl entries for the voucher
	"""
	for t in gl_name:
		frappe.db.sql("""UPDATE `tabGL Entry` SET is_cancelled = 1,
			modified=%s, modified_by=%s
			where voucher_type=%s and voucher_no=%s and name=%s and is_cancelled = 0""",
			(now(), frappe.session.user, voucher_type,t,voucher_no))


def make_entry(args, adv_adj, update_outstanding, from_repost=False):
	gle = frappe.new_doc("GL Entry")
	gle.update(args)
	gle.flags.ignore_permissions = 1
	gle.flags.from_repost = from_repost
	gle.flags.adv_adj = adv_adj
	gle.flags.update_outstanding = update_outstanding or 'Yes'
	gle.submit()

	if not from_repost:
		validate_expense_against_budget(args)


######################################################

@frappe.whitelist()
def get_progarms(doctype, txt, searchfield, start, page_len, filters):
	fltr = {'docstatus':1}
	if txt:
		fltr.update({"programs":txt})

	fltr.update({"student":filters.get("student")})
	data = frappe.get_all("Program Enrollment",fltr,['programs'],as_list=1)
	return data

@frappe.whitelist()
def get_sem(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"program":txt})
    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['program'],as_list=1)
    return data 

@frappe.whitelist()
def get_term(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"academic_term":txt})

    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['academic_term'],as_list=1)
    return data

@frappe.whitelist()
def get_year(doctype, txt, searchfield, start, page_len, filters):

	fltr = {'docstatus':1}
	if txt:
		fltr.update({"academic_year":txt})

	fltr.update({"student":filters.get("student")})
	data = frappe.get_all("Program Enrollment",fltr,['academic_year'],as_list=1)
	return data 

@frappe.whitelist()
def get_student_category(doctype, txt, searchfield, start, page_len, filters):
	fltr = {}
	lst = []
	if txt:
		fltr.update({"student_category":txt})
	fltr.update({"student":filters.get("student")})
	for i in frappe.get_all("Program Enrollment",fltr,['student_category']):
		if i.student_category not in lst:
			lst.append(i.student_category)
	return [(d,) for d in lst]

@frappe.whitelist()
def get_batch(doctype, txt, searchfield, start, page_len, filters):
	fltr = {'docstatus':1}
	if txt:
		fltr.update({"student_batch_name":txt})

	fltr.update({"student":filters.get("student")})
	data = frappe.get_all("Program Enrollment",fltr,['student_batch_name'],as_list=1)
	return data 	

@frappe.whitelist()
def get_program_enrollment(student):
	data=frappe.get_all("Program Enrollment",{'student':student,'docstatus':1},['name','program','programs'],limit=1)
	if len(data)>0:
		return data[0]


@frappe.whitelist()
def get_outstanding_fees(args):
	if isinstance(args, string_types):
		args = json.loads(args)
	################ Fee Component
	filter=[]

	filter.append(["Student","=",args.get('party')])
	filter.append(['posting_date', 'between',[args.get('from_posting_date'),args.get('to_posting_date')]])
	filter.append(["outstanding_amount",">",0])	
	filter.append(["docstatus","=",1])

	if args.get('outstanding_amt_greater_than') > 0:
		filter.append(["outstanding_amount",">",args.get('outstanding_amt_greater_than')])
	if args.get('outstanding_amt_less_than') >0:
		filter.append(["outstanding_amount","<",args.get('outstanding_amt_less_than')])	
	if args.get('cost_center'):
		filter.append(['cost_center',"=",args.get('cost_center')])	
	
	if args.get('from_due_date') and args.get('to_due_date'):
		filter.append(['valid From','between',[args.get('from_due_date'),args.get('to_due_date')]])
		filter.append(['valid_to','between',[args.get('from_due_date'),args.get('to_due_date')]])

	fees_info=frappe.db.get_all("Fees",filter,['name','posting_date'])
	######################### end fees
	fee_component_info=[]
	for t in fees_info:

		fee_component=frappe.db.get_all("Fee Component", {"parent":t['name']},
									["name","fees_category","outstanding_fees","receivable_account","income_account","amount","description",
									'grand_fee_amount','percentage','total_waiver_amount','waiver_type','waiver_amount'])
		for j in fee_component:
			if j["outstanding_fees"]>0:	
				j['posting_date']=t['posting_date']
				j['Type']='Fees'
				j['fee_voucher_no']=t['name']
				fee_component_info.append(j)	
	data=fee_component_info
	# fee_component_info [{'name': '46914acb77', 'fees_category': 'Development Fees', 'outstanding_fees': 5800.0, 'receivable_account': 'Development Fees - KP', 'income_account': 'Development Fees Income - KP', 'amount': 5800.0, 'posting_date': datetime.date(2022, 4, 27), 'Type': 'Fees', 'reference_name': 'EDU-FEE-2022-00051'}, {'name': '21f7da294d', 'fees_category': 'Development Fees', 'outstanding_fees': 5800.0, 'receivable_account': 'Development Fees - KP', 'income_account': 'Development Fees Income - KP', 'amount': 5800.0, 'posting_date': datetime.date(2022, 4, 21), 'Type': 'Fees', 'reference_name': 'EDU-FEE-2022-00010'}]

	if not data:
		frappe.msgprint(_("No outstanding invoices found for the {0} {1} which qualify the filters you have specified.")
			.format(_(args.get("party_type")).lower(), frappe.bold(args.get("party"))))

	return data		