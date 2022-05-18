# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

from cgi import print_form
import frappe
from frappe.model.document import Document
from six import iteritems, string_types
import json
from frappe.utils import cint, cstr, flt, formatdate, getdate, now
from erpnext.accounts.doctype.budget.budget import validate_expense_against_budget
from frappe.utils import money_in_words
import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from frappe.model.meta import get_field_precision

class ClosedAccountingPeriod(frappe.ValidationError): pass

class get_gl_dict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)


class FeeWaiver(Document):

	def validate(self):
		self.calculate_total()
		self.set_missing_accounts_and_fields()
		fiscal_year=frappe.get_all("Fiscal Year",filters=[["year_start_date","<=",self.posting_date],["year_end_date",">=",self.posting_date]],fields=['name'])	
		if len(fiscal_year)==0:
			frappe.throw("Fiscal Year not maintained")
		


	def on_submit(self):
		gl_cancelation(self)
		self.make_gl_entries_waiver()
		update_fee(self)


	def calculate_total(self):
		"""Calculates total amount."""
		self.grand_total = 0
		self.outstanding_amount=0
		for d in self.fee_componemts:
			self.grand_total += d.total_waiver_amount
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
	def make_gl_entries_waiver(self):
		if not self.grand_total:
			return
		data = frappe.get_all("Fee Waiver Components",{"parent":self.name},['fees_category','amount','waiver_type','percentage',
																	'waiver_amount','total_waiver_amount','receivable_account','income_account',
																	'company','grand_fee_amount','outstanding_fees','waiver_account','fee_voucher_no'
																])
		fiscal_year=frappe.get_all("Fiscal Year",filters=[["year_start_date","<=",self.posting_date],["year_end_date",">=",self.posting_date]],fields=['name'])																											
		for fc in data:
			student_gl_entries=get_gl_dict({'company': self.company, 
			'posting_date': self.posting_date, 
			'fiscal_year': fiscal_year[0]['name'], 
			'voucher_type': 'Fees', 
			'voucher_no': fc['fee_voucher_no'], 
			'remarks': None, 
			'debit': fc['grand_fee_amount'], 
			'credit': 0, 
			'debit_in_account_currency':fc['grand_fee_amount'], 
			'credit_in_account_currency': 0, 
			'is_opening': 'No', 
			'party_type': 'Student', 
			'party': self.student, 
			'project': None, 
			'post_net_value': None, 
			'account': fc['receivable_account'], 
			'against': fc['income_account'], 
			'against_voucher':fc['fee_voucher_no'], 
			'against_voucher_type': 'Fees', 
			'account_currency': 'INR'}) # This gl will be one entry
			### Fees entry without waiver part
			fee_gl_entry=get_gl_dict({'company': self.company, 
			'posting_date':self.posting_date, 
			'fiscal_year': fiscal_year[0]['name'], 
			'voucher_type': 'Fees', 
			'voucher_no':fc['fee_voucher_no'], 
			'remarks': None, 
			'debit': 0, 
			'credit': fc['grand_fee_amount']-fc['waiver_amount'], 
			'debit_in_account_currency': 0, 
			'credit_in_account_currency': fc['grand_fee_amount']-fc['waiver_amount'], 
			'is_opening': 'No', 
			'party_type': None, 
			'party': None, 
			'project': None, 
			'post_net_value': None, 
			'account': fc['income_account'], 
			'against': self.student, 
			'cost_center': self.cost_center, 
			'account_currency': 'INR'}) # one entry 
			################### end 
			waiver_fee_gl_entry=get_gl_dict({'company': self.company, 
			'posting_date':self.posting_date, 
			'fiscal_year':fiscal_year[0]['name'], 
			'voucher_type': 'Fees', 
			'voucher_no':fc['fee_voucher_no'], 
			'remarks': None, 
			'debit': 0, 
			'credit': fc['waiver_amount'], 
			'debit_in_account_currency': 0, 
			'credit_in_account_currency': fc['waiver_amount'], 
			'is_opening': 'No', 
			'party_type': None, 
			'party': None, 
			'project': None, 
			'post_net_value': None, 
			'account': fc['waiver_account'], 
			'against': self.student, 
			'cost_center': self.cost_center, 
			'account_currency': 'INR'})
			###########################
			make_gl_entries([student_gl_entries,waiver_fee_gl_entry, fee_gl_entry], cancel=(self.docstatus == 2),update_outstanding="Yes", merge_entries=False)

def update_fee(self):
	for t in self.get('fee_componemts'):
		data=frappe.get_all("Fee Component",filters=[["parent","=",t.fee_voucher_no],['fees_category','=',t.fees_category]],fields=["name",'outstanding_fees'])
		fee_data=frappe.get_all("Fees",filters=[['name','=',t.fee_voucher_no]],fields=["name","outstanding_amount"])
		outsatnding_amount=t.outstanding_fees
		waiver_type=t.waiver_type
		percentage=t.percentage
		amount=t.amount
		waiver_amount=t.waiver_amount
		total_waiver_amount=t.total_waiver_amount
		frappe.db.set_value("Fee Component",data[0]["name"], "waiver_type",str(waiver_type))
		if waiver_type=="Amount":
			frappe.db.set_value("Fee Component",data[0]["name"], "waiver_amount",waiver_amount)
		if waiver_type=="Percentage":
			frappe.db.set_value("Fee Component",data[0]["name"], "percentage",percentage)
		frappe.db.set_value("Fee Component",data[0]["name"], "total_waiver_amount",total_waiver_amount) 	
		frappe.db.set_value("Fee Component",data[0]["name"], "outstanding_fees",outsatnding_amount) 
		frappe.db.set_value("Fee Component",data[0]["name"], "amount",amount) 
		frappe.db.set_value("Fee Component",data[0]["name"], "outstanding_fees",outsatnding_amount)
		frappe.db.set_value("Fees",t.fee_voucher_no, "outstanding_amount",fee_data[0]["outstanding_amount"]-waiver_amount) 






######################################################################################################

def make_gl_entries(gl_map, cancel=False, adv_adj=False, merge_entries=True, update_outstanding='Yes', from_repost=False):
	if gl_map:
		if not cancel:
			validate_accounting_period(gl_map)
			gl_map = process_gl_map(gl_map, merge_entries)
			if gl_map and len(gl_map) > 1:
				save_entries(gl_map, adv_adj, update_outstanding, from_repost)
			# Post GL Map proccess there may no be any GL Entries
			elif gl_map:
				frappe.throw(_("Incorrect number of General Ledger Entries found. You might have selected a wrong Account in the transaction."))
		else:
			make_reverse_gl_entries_fees(gl_map, adv_adj=adv_adj, update_outstanding=update_outstanding)



def validate_accounting_period_fees(gl_map):
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
				'date': gl_map[0]['posting_date'],
				'company': gl_map[0]['company'],
				'voucher_type': gl_map[0]['voucher_type']
			}, as_dict=1)

	if accounting_periods:
		frappe.throw(_("You cannot create or cancel any accounting entries with in the closed Accounting Period {0}")
			.format(frappe.bold(accounting_periods[0].name)), ClosedAccountingPeriod)


def process_gl_map(gl_map, merge_entries=True, precision=None): ##################### cont
	if merge_entries:
		gl_map = merge_similar_entries(gl_map, precision)
	for entry in gl_map:
		# toggle debit, credit if negative entry
		if flt(entry.debit) < 0:
			entry.credit = flt(entry.credit) - flt(entry.debit)
			entry.debit = 0.0

		if flt(entry.debit_in_account_currency) < 0:
			entry.credit_in_account_currency = \
				flt(entry.credit_in_account_currency) - flt(entry.debit_in_account_currency)
			entry.debit_in_account_currency = 0.0

		if flt(entry.credit) < 0:
			entry.debit = flt(entry.debit) - flt(entry.credit)
			entry.credit = 0.0

		if flt(entry.credit_in_account_currency) < 0:
			entry.debit_in_account_currency = \
				flt(entry.debit_in_account_currency) - flt(entry.credit_in_account_currency)
			entry.credit_in_account_currency = 0.0

		update_net_values(entry)

	return gl_map


def merge_similar_entries(gl_map, precision=None):
	merged_gl_map = []
	accounting_dimensions = get_accounting_dimensions()
	for entry in gl_map:
		# if there is already an entry in this account then just add it
		# to that entry
		same_head = check_if_in_list(entry, merged_gl_map, accounting_dimensions)
		if same_head:
			same_head.debit	= flt(same_head.debit) + flt(entry.debit)
			same_head.debit_in_account_currency	= \
				flt(same_head.debit_in_account_currency) + flt(entry.debit_in_account_currency)
			same_head.credit = flt(same_head.credit) + flt(entry.credit)
			same_head.credit_in_account_currency = \
				flt(same_head.credit_in_account_currency) + flt(entry.credit_in_account_currency)
		else:
			merged_gl_map.append(entry)

	company = gl_map[0].company if gl_map else erpnext.get_default_company()
	company_currency = erpnext.get_company_currency(company)

	if not precision:
		precision = get_field_precision(frappe.get_meta("GL Entry").get_field("debit"), company_currency)

	# filter zero debit and credit entries
	merged_gl_map = filter(lambda x: flt(x.debit, precision)!=0 or flt(x.credit, precision)!=0, merged_gl_map)
	merged_gl_map = list(merged_gl_map)

	return merged_gl_map



def check_if_in_list(gle, gl_map, dimensions=None):
	account_head_fieldnames = ['voucher_detail_no', 'party', 'against_voucher',
			'cost_center', 'against_voucher_type', 'party_type', 'project', 'finance_book']

	if dimensions:
		account_head_fieldnames = account_head_fieldnames + dimensions

	for e in gl_map:
		same_head = True
		if e.account != gle.account:
			same_head = False
			continue

		for fieldname in account_head_fieldnames:
			if cstr(e.get(fieldname)) != cstr(gle.get(fieldname)):
				same_head = False
				break

		if same_head:
			return e

def update_net_values(entry):
	# In some scenarios net value needs to be shown in the ledger
	# This method updates net values as debit or credit
	if entry.post_net_value and entry.debit and entry.credit:
		if entry.debit > entry.credit:
			entry.debit = entry.debit - entry.credit
			entry.debit_in_account_currency = entry.debit_in_account_currency \
				- entry.credit_in_account_currency
			entry.credit = 0
			entry.credit_in_account_currency = 0
		else:
			entry.credit = entry.credit - entry.debit
			entry.credit_in_account_currency = entry.credit_in_account_currency \
				- entry.debit_in_account_currency

			entry.debit = 0
			entry.debit_in_account_currency = 0





def make_reverse_gl_entries_fees(gl_entries=None, voucher_type=None, voucher_no=None,
	adv_adj=False, update_outstanding="Yes"):
	"""
		Get original gl entries of the voucher
		and make reverse gl entries by swapping debit and credit
	"""

	if not gl_entries:
		gl_entries = frappe.get_all("GL Entry",
			fields = ["*"],
			filters = {
				"voucher_type": voucher_type,
				"voucher_no": voucher_no,
				"is_cancelled": 0
			})

	if gl_entries:
		validate_accounting_period(gl_entries)
		check_freezing_date(gl_entries[0]["posting_date"], adv_adj)
		set_as_cancel(gl_entries[0]['voucher_type'], gl_entries[0]['voucher_no'])

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

def save_entries(gl_map, adv_adj, update_outstanding, from_repost=False):
	if not from_repost:
		validate_cwip_accounts(gl_map)

	round_off_debit_credit(gl_map)

	if gl_map:
		check_freezing_date(gl_map[0]["posting_date"], adv_adj)

	for entry in gl_map:
		make_entry(entry, adv_adj, update_outstanding, from_repost) ######### problem

def round_off_debit_credit(gl_map):
	precision = get_field_precision(frappe.get_meta("GL Entry").get_field("debit"),
		currency=frappe.get_cached_value('Company',  gl_map[0].company,  "default_currency"))

	debit_credit_diff = 0.0
	for entry in gl_map:
		entry.debit = flt(entry.debit, precision)
		entry.credit = flt(entry.credit, precision)
		debit_credit_diff += entry.debit - entry.credit

	debit_credit_diff = flt(debit_credit_diff, precision)

	if gl_map[0]["voucher_type"] in ("Journal Entry", "Payment Entry"):
		allowance = 5.0 / (10**precision)
	else:
		allowance = .5

	if abs(debit_credit_diff) > allowance:
		frappe.throw(_("Debit and Credit not equal for {0} #{1}. Difference is {2}.")
			.format(gl_map[0].voucher_type, gl_map[0].voucher_no, debit_credit_diff))

	elif abs(debit_credit_diff) >= (1.0 / (10**precision)):
		make_round_off_gle(gl_map, debit_credit_diff, precision)

def validate_cwip_accounts(gl_map):
	"""Validate that CWIP account are not used in Journal Entry"""
	if gl_map and gl_map[0].voucher_type != "Journal Entry":
		return

	cwip_enabled = any(cint(ac.enable_cwip_accounting) for ac in frappe.db.get_all("Asset Category", "enable_cwip_accounting"))
	if cwip_enabled:
		cwip_accounts = [d[0] for d in frappe.db.sql("""select name from tabAccount
			where account_type = 'Capital Work in Progress' and is_group=0""")]

		for entry in gl_map:
			if entry.account in cwip_accounts:
				frappe.throw(
					_("Account: <b>{0}</b> is capital Work in progress and can not be updated by Journal Entry").format(entry.account))
					
def make_round_off_gle(gl_map, debit_credit_diff, precision):
	round_off_account, round_off_cost_center = get_round_off_account_and_cost_center(gl_map[0].company)
	round_off_account_exists = False
	round_off_gle = frappe._dict()
	for d in gl_map:
		if d.account == round_off_account:
			round_off_gle = d
			if d.debit:
				debit_credit_diff -= flt(d.debit)
			else:
				debit_credit_diff += flt(d.credit)
			round_off_account_exists = True

	if round_off_account_exists and abs(debit_credit_diff) <= (1.0 / (10**precision)):
		gl_map.remove(round_off_gle)
		return

	if not round_off_gle:
		for k in ["voucher_type", "voucher_no", "company",
			"posting_date", "remarks"]:
				round_off_gle[k] = gl_map[0][k]

	round_off_gle.update({
		"account": round_off_account,
		"debit_in_account_currency": abs(debit_credit_diff) if debit_credit_diff < 0 else 0,
		"credit_in_account_currency": debit_credit_diff if debit_credit_diff > 0 else 0,
		"debit": abs(debit_credit_diff) if debit_credit_diff < 0 else 0,
		"credit": debit_credit_diff if debit_credit_diff > 0 else 0,
		"cost_center": round_off_cost_center,
		"party_type": None,
		"party": None,
		"is_opening": "No",
		"against_voucher_type": None,
		"against_voucher": None
	})

	if not round_off_account_exists:
		gl_map.append(round_off_gle)

def get_round_off_account_and_cost_center(company):
	round_off_account, round_off_cost_center = frappe.get_cached_value('Company',  company,
		["round_off_account", "round_off_cost_center"]) or [None, None]
	if not round_off_account:
		frappe.throw(_("Please mention Round Off Account in Company"))

	if not round_off_cost_center:
		frappe.throw(_("Please mention Round Off Cost Center in Company"))

	return round_off_account, round_off_cost_center
###################################################################################################
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