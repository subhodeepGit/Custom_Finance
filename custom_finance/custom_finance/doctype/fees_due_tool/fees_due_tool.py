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
	
	return fees
	
# Bulk Email
@frappe.whitelist()
def get_student_emails(studentss):
	studentss=json.loads(studentss)
	recipients=""
	for stu in studentss:
		recipients=recipients+","+stu['student_email_id']
	return recipients

