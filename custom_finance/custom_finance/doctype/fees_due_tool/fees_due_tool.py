# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.document import Document
from pytz import all_timezones, country_names
from frappe.utils.data import nowtime
from frappe.utils.background_jobs import enqueue
from frappe.utils import cint, flt, cstr
from frappe import _


class FeesDueTool(Document):
	pass
# Fetch all student data whose fees is due
@frappe.whitelist()
def get_students(academic_term=None, programs=None, program=None, academic_year=None):
	fees=frappe.db.sql(""" Select name,student,student_name,student_email,outstanding_amount from `tabFees`
	where outstanding_amount > 0 and programs="%s" and program="%s" and academic_term="%s" and academic_year="%s"
	"""%(programs,program,academic_term,academic_year),as_dict = True)
	
	# return fees
	if len(fees)!=0:
		return fees
	else:
		frappe.throw("All Due Fees is Clear/Fees is not created")
		
# Bulk Email For Student
@frappe.whitelist()
def get_student_emails(studentss):
	studentss=json.loads(studentss)
	recipients=""
	for stu in studentss:
			recipients+=(frappe.db.get_value("Student",{"name":stu.get("students")},"student_email_id")+",")
	return recipients

# Bulk Email For Guardian
@frappe.whitelist()
def get_guardian_emails(studentss):
	studentss=json.loads(studentss)
	recipients=""
	for stu in studentss:
			gud_info=frappe.db.get_value("Student",{"name":stu.get("students")},"guardian_email_address")
			if gud_info!=None:
				recipients+=(frappe.db.get_value("Student",{"name":stu.get("students")},"guardian_email_address")+",")
	if recipients=="":
		frappe.throw("Guardian Email id not Found (Please mention in Student Data)")			
	return recipients

# Bulk Email For Both
@frappe.whitelist()
def get_both_emails(studentss):
	studentss=json.loads(studentss)
	recipients=""
	for stu in studentss:
		gud_info=frappe.db.get_value("Student",{"name":stu.get("students")},"guardian_email_address")
		if gud_info!=None:
			recipients+=(frappe.db.get_value("Student",{"name":stu.get("students")},"student_email_id")+",")
			recipients+=(frappe.db.get_value("Student",{"name":stu.get("students")},"guardian_email_address")+",")
	if recipients=="":
		frappe.throw("Guardian Email id not Found (Please mention in Student Data)")			
	return recipients
