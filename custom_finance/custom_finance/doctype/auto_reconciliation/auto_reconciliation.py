# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

from dataclasses import fields
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.utils import cstr

class AutoReconciliation(Document):
	def validate(self):
		student_reference=self.get("student_reference")
		if not student_reference:
			frappe.throw("No record found in Student Reference Table")
	
	@frappe.whitelist()		
	def create_payment_entry(self):
		self.db_set("payment_status", "In Process")
		frappe.publish_realtime("fee_schedule_progress",
			{"progress": "0", "reload": 1}, user=frappe.session.user)
		total_records=len(self.get("student_reference"))
		if total_records > 10:
			frappe.msgprint(_('''Payment records will be created in the background.
				In case of any error the error message will be updated in the Schedule.'''))
			enqueue(generate_payment, queue='default', timeout=6000, event='generate_payment',
				fee_schedule=self.name)
		else:
			generate_payment(self.name)	
					
def generate_payment(payment_schedule):
	print("\n\n\n\n\n\n")
	print(payment_schedule)
	doc = frappe.get_doc("Auto Reconciliation", payment_schedule)
	print(doc)
	error = False
	print(doc.name)
	for t in doc.get("student_reference"):
		outstanding_amount=t.outstanding_amount
		if outstanding_amount!=0:
			pass
		elif outstanding_amount!=0:
			try:
				pass
			except Exception as e:
				error = True
				err_msg = frappe.local.message_log and "\n\n".join(frappe.local.message_log) or cstr(e)

	if error:
		frappe.db.rollback()
		frappe.db.set_value("Auto Reconciliation", payment_schedule, "payment_status", "Failed")
		frappe.db.set_value("Fee Schedule", payment_schedule, "error_log", err_msg)

	else:
		frappe.db.set_value("Auto Reconciliation", payment_schedule, "payment_status", "Successful")
		frappe.db.set_value("Auto Reconciliation", payment_schedule, "error_log", None)

	frappe.publish_realtime("fee_schedule_progress",
		{"progress": "100", "reload": 1}, user=frappe.session.user)







@frappe.whitelist()
def get_fees(date=None,type_of_transaction=None):
	stud_payment_upload=frappe.get_all("Payment Details Upload",filters=[["date_of_transaction","=",date],['type_of_transaction','=',type_of_transaction],
											["reconciliation_status","=",1],["reconciliation_status","=",1],["payment_status","=",0],['docstatus',"=",1]],
											fields=['name','student','unique_transaction_reference_utr','amount',"remarks","reconciliation_status", "student_name"])
	stu_info=[]
	for t in stud_payment_upload:
		stu_info.append(t['student'])										
	stu_info = list(set(stu_info))

	for t in stu_info:
		outstanding_amount=0
		fees=frappe.get_all("Fees",filters=[["student","=",t],['outstanding_amount',">",0],['docstatus',"=",1]],fields=['name',"outstanding_amount"])
		if fees:
			for z in fees:
				outstanding_amount=outstanding_amount+z["outstanding_amount"]
		for y in stud_payment_upload:
			if y["student"]==t:
				y['outstanding_amount']=outstanding_amount		
	return stud_payment_upload										