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
		if mode_of_payment:
			mode_of_parent=frappe.get_all("Mode of Payment",{"name":self.type_of_transaction},['enabled'])
			if 	mode_of_parent[0]['enabled']!=1:
				frappe.throw("Mode of payment is Disabled for the mode of payment "+self.type_of_transaction)

	
	@frappe.whitelist()		
	def create_payment_entry(self):
		self.db_set("payment_status", "In Process")
		frappe.publish_realtime("fee_schedule_progress",
			{"progress": "0", "reload": 1}, user=frappe.session.user)
		total_records=len(self.get("student_reference"))
		if total_records > 150:
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
		outstanding_amount=t.outstanding_amount
		amount=t.amount
		if outstanding_amount!=0:
			try:
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
				payment_entry.paid_from_account_type=account_cur[0]['account_type']
				payment_entry.paid_from_account_currency=account_cur[0]['account_currency']
				payment_entry.target_exchange_rate=1
				"""Amount"""
				payment_entry.paid_amount=amount
				payment_entry.received_amount = amount
				"""Reference"""
				############### structured fees
				fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",t.student],["outstanding_amount","!=",0],
															["fee_structure","!=",""],["hostel_fee_structure","=",""],["docstatus","=",1]],
															fields=['name','due_date','program','company'],
															order_by="due_date asc")																		
				structured_fees=[]
				for t1 in fee_voucher_list:
					due_date=t1['due_date']
					program=t1['program']
					fee_comp=frappe.get_all("Fee Component",filters=[["parent","=",t1['name']],["outstanding_fees","!=",0]],
											fields=['name','idx','parent','fees_category','description','amount','waiver_type',
													'percentage','waiver_amount','total_waiver_amount','receivable_account','income_account',
													'company','grand_fee_amount','outstanding_fees'])
					for z in fee_comp:
						z['due_date']=due_date
						z['program']=program
						structured_fees.append(z)
				if fee_voucher_list:		
					structured_fees = sorted(structured_fees , key=lambda elem: "%02d %s" % (elem['idx'], elem['due_date']))		
				structured_fees_hostel=[]
				hostel_fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",t.student],["outstanding_amount","!=",0],
															["hostel_fee_structure","!=",""],["fee_structure","=",""],["docstatus","=",1]],
															fields=['name','due_date','program'],order_by="due_date asc")										
				for t1 in hostel_fee_voucher_list:
					due_date=t1['due_date']
					program=t1['program']
					fee_comp=frappe.get_all("Fee Component",filters=[["parent","=",t1['name']],["outstanding_fees","!=",0]],
											fields=['name','idx','parent','fees_category','description','amount','waiver_type',
													'percentage','waiver_amount','total_waiver_amount','receivable_account','income_account',
													'company','grand_fee_amount','outstanding_fees'])
					for z in fee_comp:
						z['due_date']=due_date
						z['program']=program
						structured_fees_hostel.append(z)
				if 	hostel_fee_voucher_list:	
					structured_fees_hostel = sorted(structured_fees_hostel , key=lambda elem: "%02d %s" % (elem['idx'], elem['due_date']))
				structured_fees=structured_fees+structured_fees_hostel


				########################################## end of structured fees
				#################### unstructured fees hostel
				unstructured_fees_hostel=[]
				unstructured_fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",t.student],["outstanding_amount","!=",0],
															["hostel_fee_structure","=",""],["fee_structure","=",""],["docstatus","=",1]],
															fields=['name','due_date','program'],order_by="due_date asc")											
				for t1 in unstructured_fee_voucher_list:
					due_date=t1['due_date']
					program=t1['program']
					fee_comp=frappe.get_all("Fee Component",filters=[["parent","=",t1['name']],["outstanding_fees","!=",0]],
											fields=['name','idx','parent','fees_category','description','amount','waiver_type',
													'percentage','waiver_amount','total_waiver_amount','receivable_account','income_account',
													'company','grand_fee_amount','outstanding_fees'])
					for z in fee_comp:
						z['due_date']=due_date
						z['program']=program
						unstructured_fees_hostel.append(z)
				if 	unstructured_fees_hostel:	
					unstructured_fees_hostel = sorted(unstructured_fees_hostel , key=lambda elem: "%02d %s" % (elem['idx'], elem['due_date']))
				structured_fees=structured_fees+unstructured_fees_hostel

				########################################## end unstructured fees hostel
				allocate_amount=amount
				for t1 in structured_fees:
					outstanding_fees_allocation=allocate_amount-t1['outstanding_fees']
					if outstanding_fees_allocation>0:
						allocate_amount=outstanding_fees_allocation
						payment_entry.append("references", {
								'reference_doctype': "Fees",
								'reference_name': t1['parent'],
								"bill_no": "",
								"due_date":t1['due_date'],
								'total_amount': t1["outstanding_fees"],
								'outstanding_amount': t1["outstanding_fees"],
								'allocated_amount': t1["outstanding_fees"],
								'program':t1["program"],
								'fees_category':t1['fees_category'],
								'account_paid_from':t1['receivable_account'],
							})
					elif outstanding_fees_allocation<=0:
						payment_entry.append("references", {
								'reference_doctype': "Fees",
								'reference_name': t1['parent'],
								"bill_no": "",
								"due_date":t1['due_date'],
								'total_amount': t1["outstanding_fees"],
								'outstanding_amount': t1["outstanding_fees"],
								'allocated_amount': allocate_amount,
								'program':t1["program"],
								'fees_category':t1['fees_category'],
								'account_paid_from':t1['receivable_account'],
							})
						break


				# "references"-- table name	 Payment Entry Reference		

				"""Writeoff"""
				payment_entry.total_allocated_amount=amount
				payment_entry.unallocated_amount=0
				payment_entry.difference_amount=0
				payment_entry.base_total_taxes_and_charges=0
				"""Transaction ID"""
				payment_entry.reference_no=t.utr_no
				payment_entry.reference_date=data_of_clearing
				"""Cost Center"""
				cost_cente=frappe.get_all("Company",['cost_center'])
				payment_entry.cost_center=cost_cente[0]['cost_center']
				payment_entry.save()
				payment_entry.submit()
				frappe.db.set_value("Auto Reconciliation child",t.name,"payment_voucher",payment_entry.name)
				###################### end
			except Exception as e:
				error = True
				err_msg = frappe.local.message_log and "\n\n".join(frappe.local.message_log) or cstr(e)
 
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
				cost_cente=frappe.get_all("Company",['cost_center'])
				payment_refund.cost_center=cost_cente[0]['cost_center']
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
	if type_of_transaction=="Online Payment":
		stud_payment_upload_1=frappe.get_all("ICICI Online Payment",filters=[["posting_date","=",date],["transaction_status","=","SUCCESS"],
													["transaction_status","=","SUCCESS"],["payment_status","=",0]],
												fields=["name","party","transaction_id","paying_amount","payment_status","party_name","remarks"])
		stu_info=[]
		for t in stud_payment_upload_1:
			stu_info.append(t['party'])										
		stu_info = list(set(stu_info))
		
		for t in stu_info:
			outstanding_amount=0
			fees=frappe.get_all("Fees",filters=[["student","=",t],['outstanding_amount',">",0],['docstatus',"=",1]],fields=['name',"outstanding_amount"])
			if fees:
				for z in fees:
					outstanding_amount=outstanding_amount+z["outstanding_amount"]
			for y in stud_payment_upload_1:
				if y["party"]==t:
					y['outstanding_amount']=outstanding_amount	
		stud_payment_upload=stud_payment_upload_1
	return stud_payment_upload										