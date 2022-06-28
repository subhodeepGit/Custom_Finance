# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

from dataclasses import fields
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.utils import cstr
from frappe import utils

class AutoReconciliation(Document):
	def validate(self):
		student_reference=self.get("student_reference")
		if not student_reference:
			frappe.throw("No record found in Student Reference Table")
		mode_of_payment=frappe.get_all("Mode of Payment Account",{"parent":self.type_of_transaction},["name","parent","default_account"])
		if not 	mode_of_payment:
			frappe.throw("Account not manatained for the mode of payment")

	
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
	doc = frappe.get_doc("Auto Reconciliation", payment_schedule)
	data_of_clearing=doc.data_of_clearing
	error = False
	for t in doc.get("student_reference"):
		print("\n\n\n\n\n\n\n")
		outstanding_amount=t.outstanding_amount
		amount=t.amount
		if outstanding_amount!=0:
			############################################### Data entry in Payment entry
			payment_entry=frappe.new_doc("Payment Entry")
			"""Type of Payment"""
			payment_entry.payment_type="Receive"
			payment_entry.posting_date=utils.today()
			payment_entry.mode_of_payment=doc.type_of_transaction
			"""Payment From / To"""
			# student_email_id=frappe.get_all("Student",{"name":t.student},["student_email_id","sams_portal_id","roll_no"])
			payment_entry.party_type="Student"
			payment_entry.party=t.student
			payment_entry.party_name=t.student_name
			# payment_entry.student_email=student_email_id[0]["student_email_id"]
			# payment_entry.sams_portal_id=student_email_id[0]["sams_portal_id"]
			"""Accounts"""
			mode_of_payment=frappe.get_all("Mode of Payment Account",{"parent":doc.type_of_transaction},["name","parent","default_account"])
			account_cur=frappe.get_all("Account",{"name":mode_of_payment[0]["default_account"]},['account_currency',"account_type"])
			payment_entry.paid_to=mode_of_payment[0]['default_account']
			payment_entry.paid_to_account_currency=account_cur[0]['account_currency']
			payment_entry.paid_to_account_type=account_cur[0]['account_type']
			payment_entry.source_exchange_rate=1
			# Cash - KP  paid_from_account_type
			paid_from="Cash - KP"
			account_cur=frappe.get_all("Account",{"name":paid_from},['account_currency',"account_type"])
			payment_entry.paid_from=paid_from
			payment_entry.paid_from_account_type=account_cur[0]['account_currency']
			payment_entry.paid_from_account_currency=account_cur[0]['account_type']
			payment_entry.target_exchange_rate=1
			"""Amount"""
			payment_entry.paid_amount=amount
			"""Reference"""
			############### structured fees
			fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",t.student],["outstanding_amount","!=",0],
														["fee_structure","!=",""]],fields=['name','due_date'],order_by="due_date asc")
			print("\n\n\n\n\n")
			print(fee_voucher_list)
			structured_fees=[]
			for t in fee_voucher_list:
				due_date=t['due_date']
				fee_comp=frappe.get_all("Fee Component",filters=[["parent","=",t['name']]],fields=['name','idx','parent','fees_category','description','amount','waiver_type',
																									'percentage','waiver_amount','total_waiver_amount','receivable_account','income_account',
																									'company','grand_fee_amount','outstanding_fees'])
				for z in fee_comp:
					z['due_date']=due_date
					structured_fees.append(z)
			structured_fees = sorted(structured_fees , key=lambda elem: "%02d %s" % (elem['idx'], elem['due_date']))
			print("\n\n\n\n\n")
			print("structured_fees",structured_fees)		
			# a=[{'name': 'Bart', 'age': 10}, {'name': 'Abhishek', 'age': 39}]
			# newlist = sorted(a, key=lambda d: d['name']) 
			# print(newlist)
			
			"""Writeoff"""
			payment_entry.total_allocated_amount=amount
			payment_entry.unallocated_amount=0
			payment_entry.difference_amount=0
			payment_entry.base_total_taxes_and_charges=0
			"""Cost Center"""
			payment_entry.cost_center="Main - KP"
			# payment_entry.save()
			# payment_entry.submit()
			# frappe.db.set_value("Auto Reconciliation child",t.name,"payment_voucher",payment_entry.name)
			###################### end 
		elif outstanding_amount==0: ##### testing correction
			try:
				############################# data entry in payment Refund Entry 
				payment_refund=frappe.new_doc("Payment Refund")
				"""Type of Payment"""
				payment_refund.payment_type="Receive"
				payment_refund.posting_date=utils.today()
				payment_refund.mode_of_payment=doc.type_of_transaction
				"""Payment From / To"""
				payment_refund.party_type="Student"
				payment_refund.party=t.student
				payment_refund.party_name=t.student_name
				student_email_id=frappe.get_all("Student",{"name":t.student},["student_email_id","sams_portal_id"])
				payment_refund.student_email=student_email_id[0]["student_email_id"]
				payment_refund.sams_portal_id=student_email_id[0]["sams_portal_id"]
				"""Accounts"""
				mode_of_payment=frappe.get_all("Mode of Payment Account",{"parent":doc.type_of_transaction},["name","parent","default_account"])
				account_cur=frappe.get_all("Account",{"name":mode_of_payment[0]["default_account"]},['account_currency'])
				payment_refund.paid_from=mode_of_payment[0]['default_account']
				payment_refund.paid_from_account_type=account_cur[0]['account_currency']
				"""Reference"""
				account=frappe.get_all("Account",filters=[["name","like","%Fees Refundable / Adjustable%"],
															["account_type","=","Income Account"]],fields=['name'])										
				payment_refund.append("references",{
					"fees_category":"Fees Refundable / Adjustable",
					"account_paid_to":account[0]['name'],
					"allocated_amount":amount,
					"total_amount":amount
				})
				"""Accounting Dimensions"""
				payment_refund.cost_center="Main - KP"
				"""Transaction ID"""
				payment_refund.reference_no=t.utr_no
				payment_refund.reference_date=data_of_clearing
				payment_refund.save()
				payment_refund.submit()
				frappe.db.set_value("Auto Reconciliation child",t.name,"payment_voucher",payment_refund.name)
				############################## End 
			except Exception as e:
				error = True
				err_msg = frappe.local.message_log and "\n\n".join(frappe.local.message_log) or cstr(e)

	# if error:
	# 	frappe.db.rollback()
	# 	frappe.db.set_value("Auto Reconciliation", payment_schedule, "payment_status", "Failed")
	# 	frappe.db.set_value("Fee Schedule", payment_schedule, "error_log", err_msg)

	# else:
	# 	frappe.db.set_value("Auto Reconciliation", payment_schedule, "payment_status", "Successful")
	# 	frappe.db.set_value("Auto Reconciliation", payment_schedule, "error_log", None)

	# frappe.publish_realtime("fee_schedule_progress",
	# 	{"progress": "100", "reload": 1}, user=frappe.session.user)







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