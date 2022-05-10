# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from six import iteritems, string_types
import json

class FeeWaiver(Document):
	pass



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
	print("\n\n\n\n\n")
	print("ok")
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
									["name","fees_category","outstanding_fees","receivable_account","income_account","outstanding_fees","amount"])
		for j in fee_component:
			if j["outstanding_fees"]>0:	
				j['posting_date']=t['posting_date']
				j['Type']='Fees'
				j['reference_name']=t['name']
				fee_component_info.append(j)	
	data=fee_component_info
	# fee_component_info [{'name': '46914acb77', 'fees_category': 'Development Fees', 'outstanding_fees': 5800.0, 'receivable_account': 'Development Fees - KP', 'income_account': 'Development Fees Income - KP', 'amount': 5800.0, 'posting_date': datetime.date(2022, 4, 27), 'Type': 'Fees', 'reference_name': 'EDU-FEE-2022-00051'}, {'name': '21f7da294d', 'fees_category': 'Development Fees', 'outstanding_fees': 5800.0, 'receivable_account': 'Development Fees - KP', 'income_account': 'Development Fees Income - KP', 'amount': 5800.0, 'posting_date': datetime.date(2022, 4, 21), 'Type': 'Fees', 'reference_name': 'EDU-FEE-2022-00010'}]

	if not data:
		frappe.msgprint(_("No outstanding invoices found for the {0} {1} which qualify the filters you have specified.")
			.format(_(args.get("party_type")).lower(), frappe.bold(args.get("party"))))

	return data		