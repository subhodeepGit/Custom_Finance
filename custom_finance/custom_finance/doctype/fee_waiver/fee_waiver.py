# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from six import iteritems, string_types
import json
from erpnext.accounts.general_ledger import make_reverse_gl_entries

class FeeWaiver(Document):
	pass
	def validate(self):
		GL_account_info=[]
		for t in self.get("fee_componemts"):
			Gl_entry=frappe.db.get_all("GL Entry",filters=[["voucher_no","=",t.fee_voucher_no],["account","=",t.receivable_account]],fields=['name','voucher_no'])
			GL_account_info.append(Gl_entry[0])
			Gl_entry=frappe.db.get_all("GL Entry",filters=[["voucher_no","=",t.fee_voucher_no],["account","=",t.income_account]],fields=['name','voucher_no'])
			GL_account_info.append(Gl_entry[0])
		print("\n\n\n\n\n")
		print(GL_account_info)
		for t in GL_account_info:
			print(t['name'])
			print(t['voucher_no'])
			make_reverse_gl_entries(gl_entries=t['name'],voucher_no=t['voucher_no'])
			# make_reverse_gl_entries(gl_entries=t['name'], voucher_type=None, voucher_no=t['voucher_no'],adv_adj=False, update_outstanding="Yes")





	# 	make_reverse_gl_entries(gl_entries='6598048b44')
	# make_reverse_gl_entries(gl_entries='', voucher_type=None, voucher_no=None,adv_adj=False, update_outstanding="Yes")
		
	# for cancelation try gl_entries
	#self.calculate_total()
	# self.set_missing_accounts_and_fields()
	# def calculate_total(self):
	# 	"""Calculates total amount."""
	# 	self.grand_total = 0
	# 	for d in self.components:
	# 		self.grand_total += d.amount
	# 	self.outstanding_amount = self.grand_total
	# 	self.grand_total_in_words = money_in_words(self.grand_total)
	# def set_missing_accounts_and_fields(self):
	# 	if not self.company:
	# 		self.company = frappe.defaults.get_defaults().company
	# 	if not self.currency:
	# 		self.currency = erpnext.get_company_currency(self.company)
	# 	################################################################	
	# 	if not (self.receivable_account and self.income_account and self.cost_center):
	# 		accounts_details = frappe.get_all("Company",
	# 			fields=["default_receivable_account", "default_income_account", "cost_center"],
	# 			filters={"name": self.company})[0]

	# 	if not self.receivable_account:
	# 		self.receivable_account = accounts_details.default_receivable_account
	# 	if not self.income_account:
	# 		self.income_account = accounts_details.default_income_account
	# 	################################################################	
	# 	if not self.cost_center:
	# 		self.cost_center = accounts_details.cost_center
	# 	if not self.student_email:
	# 		self.student_email = self.get_student_emails()
	# pass



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