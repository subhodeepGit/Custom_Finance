# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from pytz import all_timezones, country_names
from frappe.utils.data import nowtime
from frappe.utils.background_jobs import enqueue
from frappe.utils import cint, flt, cstr
from custom_finance.custom_finance.notification.custom_notification import fees_due_tool
from frappe import _


class FeesDueTool(Document):
	pass
@frappe.whitelist()
def get_students(academic_term=None, programs=None, program=None, academic_year=None):
	print("\n\n\n\n\n\n\n\n\n")
	print("hello")
	fees=frappe.db.sql(""" Select name,student,student_name,student_email,outstanding_amount from `tabFees`
	where outstanding_amount > 0 and programs="%s" and program="%s" and academic_term="%s" and academic_year="%s"
	"""%(programs,program,academic_term,academic_year),as_dict = True)
	print(fees)

	return fees

def send_email(self):
	# max_due_date = (datetime.strptime(self.due_date, '%Y-%m-%d')+timedelta(days=1)).isoformat()
	# print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
	# print(max_due_date)
	# print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")   
	# if self.outstanding_amount > 0 and self.due_date==max_due_date:
		fees_due_tool(self)