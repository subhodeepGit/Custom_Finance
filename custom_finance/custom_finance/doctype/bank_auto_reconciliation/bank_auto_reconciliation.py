# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

from dataclasses import fields
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.utils import cstr
from frappe import utils

class BankAutoReconciliation(Document):
	def validate(self):
		student_reference=self.get("student_reference")
		for t in student_reference:
			if t.amount != t.total_paying_amount:
				frappe.throw('Total Paying amount not match with Total Amount %s'%(t.student))
			if t.current_outstanding_development_fees<0 or t.current_oustanding_tuition_fees<0 or t.current_outstanding_other_institutional_fees<0  or \
				t.current_outstanding_miscellaneous_fees<0 or t.current_outstanding_examination_fees<0 or t.current_outstanding_transportation_fees<0 or \
				t.current_outstanding_counselling_fees<0 or t.current_outstanding_re_admission_fees<0 or t.current_outstanding_arrear_dues<0 \
				or t.current_outstanding_hostel_admission_fees<0 or t.current_outstanding_hostel_fees<0 or t.current_outstanding_mess_fees<0 :
					frappe.throw("Outstanding Amount can't be negative %s "%(t.student))
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
				fee_schedule=self.name,self=self)
		else:
			generate_payment(self.name,self)

def generate_payment(payment_schedule,self):
	print('\n\n\n\n\n')
	doc = frappe.get_doc("Bank Auto Reconciliation", payment_schedule)
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
					for t in self.get("student_reference"):
						# print(t.paying_tuition_fees)
						if t1['fees_category']=="Re-Admission Fees":
							allocated_amount=t.paying_re_admission_fees							
						if t1['fees_category']=="Arrear Dues":
							allocated_amount=t.paying_arrear_dues							
						if t1['fees_category']=="Tuition Fees":
							allocated_amount=t.paying_tuition_fees							
						if t1['fees_category']=="Development Fees":
							allocated_amount=t.paying_development_fees							
						if t1['fees_category']=="Hostel Admission Fees":
							allocated_amount=t.paying_hostel_admission_fees							
						if t1['fees_category']=="Counselling Fees":
							allocated_amount=t.paying_counselling_fees							
						if t1['fees_category']=="Examination Fees":
							allocated_amount=t.paying_examination_fees							
						if t1['fees_category']=="Transportation Fees":
							allocated_amount=t.paying_transportation_fees							
						if t1['fees_category']=="Mess Fees":
							allocated_amount=t.paying_mess_fees							
						if t1['fees_category']=="Miscellaneous Fees":
							allocated_amount=t.paying_miscellaneous_fees							
						if t1['fees_category']=="Hostel Fees":
							allocated_amount=t.paying_hostel_fees							
						if t1['fees_category']=="Other Institutional Fees":
							allocated_amount=t.paying_other_institutional_fees

					outstanding_fees_allocation=allocate_amount-t1['outstanding_fees']
					print(allocated_amount)
					if outstanding_fees_allocation>0:
						allocate_amount=outstanding_fees_allocation
						payment_entry.append("references", {
								'reference_doctype': "Fees",
								'reference_name': t1['parent'],
								"bill_no": "",
								"due_date":t1['due_date'],
								'total_amount': t1["outstanding_fees"],
								'allocated_amount': allocated_amount,
								'outstanding_amount': t1["outstanding_fees"]-allocated_amount,
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
								'allocated_amount': allocated_amount,
								'outstanding_amount': t1["outstanding_fees"]-allocated_amount,								
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
				# payment_entry.submit()
				frappe.db.set_value("Bank Auto Reconciliation Child",t.name,"payment_voucher",payment_entry.name)
				###################### end
			except Exception as e:
				error = True
				print(e)
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
				# payment_refund.submit()
				frappe.db.set_value("Bank Auto Reconciliation Child",t.name,"payment_voucher",payment_refund.name)
				############################## End 
			except Exception as e:
				error = True
				print(e)
				err_msg = frappe.local.message_log and "\n\n".join(frappe.local.message_log) or cstr(e)

	if error:
		frappe.db.rollback()
		frappe.db.set_value("Bank Auto Reconciliation", payment_schedule, "payment_status", "Failed")
		frappe.db.set_value("Fee Schedule", payment_schedule, "error_log", err_msg)

	else:
		frappe.db.set_value("Bank Auto Reconciliation", payment_schedule, "payment_status", "Successful")
		frappe.db.set_value("Bank Auto Reconciliation", payment_schedule, "error_log", None)

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
		payment_amount=t['amount']
	stu_info = list(set(stu_info))

	for t in stu_info:
		outstanding_amount=0
		re_admission_fees=0
		arrear_dues=0
		tuition_fees=0
		development_fees=0
		hostel_admission_fees=0
		counselling_fees=0
		examination_fees=0
		transportation_fees=0
		mess_fees=0
		miscellaneous_fees=0
		hostel_fees=0
		other_institutional_fees=0

		fees=frappe.get_all("Fees",filters=[["student","=",t],['outstanding_amount',">",0],['docstatus',"=",1]],fields=['name',"outstanding_amount"])
		if fees:
			for z in fees:
				outstanding_amount=outstanding_amount+z["outstanding_amount"]
				for j in frappe.get_all("Fee Component",{"parent":z['name']},["fees_category",'outstanding_fees']):
					if j['fees_category']=="Re-Admission Fees":
						re_admission_fees=re_admission_fees+j['outstanding_fees']
					if j['fees_category']=="Arrear Dues":
						arrear_dues=arrear_dues+j['outstanding_fees']
					if j['fees_category']=="Tuition Fees":
						tuition_fees=tuition_fees+j['outstanding_fees']
					if j['fees_category']=="Development Fees":
						development_fees=development_fees+j['outstanding_fees']
					if j['fees_category']=="Hostel Admission Fees":
						hostel_admission_fees=hostel_admission_fees+j['outstanding_fees']
					if j['fees_category']=="Counselling Fees":
						counselling_fees=counselling_fees+j['outstanding_fees']
					if j['fees_category']=="Examination Fees":
						examination_fees=examination_fees+j['outstanding_fees']
					if j['fees_category']=="Transportation Fees":
						transportation_fees=transportation_fees+j['outstanding_fees']
					if j['fees_category']=="Mess Fees":
						mess_fees=mess_fees+j['outstanding_fees']
					if j['fees_category']=="Miscellaneous Fees":
						miscellaneous_fees=miscellaneous_fees+j['outstanding_fees']
					if j['fees_category']=="Hostel Fees":
						hostel_fees=hostel_fees+j['outstanding_fees']
					if j['fees_category']=="Other Institutional Fees":
						other_institutional_fees=other_institutional_fees+j['outstanding_fees']																	
		for y in stud_payment_upload:
			if y["student"]==t:
				y['outstanding_amount']=outstanding_amount
				y['re_admission_fees']=re_admission_fees
				y['arrear_dues']=arrear_dues
				y['tuition_fees']=tuition_fees
				y['development_fees']=development_fees
				y['hostel_admission_fees']=hostel_admission_fees
				y['counselling_fees']=counselling_fees
				y['examination_fees']=examination_fees
				y['transportation_fees']=transportation_fees
				y['mess_fees']=mess_fees
				y['miscellaneous_fees']=miscellaneous_fees
				y['hostel_fees']=hostel_fees
				y['other_institutional_fees']=other_institutional_fees

				y['outstanding_amount_cal']=outstanding_amount
				y['re_admission_fees_cal']=re_admission_fees
				y['arrear_dues_cal']=arrear_dues
				y['tuition_fees_cal']=tuition_fees
				y['development_fees_cal']=development_fees
				y['hostel_admission_fees_cal']=hostel_admission_fees
				y['counselling_fees_cal']=counselling_fees
				y['examination_fees_cal']=examination_fees
				y['transportation_fees_cal']=transportation_fees
				y['mess_fees_cal']=mess_fees
				y['miscellaneous_fees_cal']=miscellaneous_fees
				y['hostel_fees_cal']=hostel_fees
				y['other_institutional_fees_cal']=other_institutional_fees
	if type_of_transaction=="Online Payment":
		stud_payment_upload_1=frappe.get_all("ICICI Online Payment",filters=[["posting_date","=",date],["transaction_status","=","SUCCESS"],
													["transaction_status","=","SUCCESS"],["payment_status","=",0]],
												fields=["name","party","transaction_id","paying_amount","payment_status","party_name","remarks"])
		stu_info=[]
		for t in stud_payment_upload_1:
			stu_info.append(t['party'])
			# paying_amount=t['paying_amount']							
		stu_info = list(set(stu_info))
		
		for t in stu_info:
			outstanding_amount=0
			re_admission_fees=0
			arrear_dues=0
			tuition_fees=0
			development_fees=0
			hostel_admission_fees=0
			counselling_fees=0
			examination_fees=0
			transportation_fees=0
			mess_fees=0
			miscellaneous_fees=0
			hostel_fees=0
			other_institutional_fees=0
			fees=frappe.get_all("Fees",filters=[["student","=",t],['outstanding_amount',">",0],['docstatus',"=",1]],fields=['name',"outstanding_amount"])
			if fees:
				for z in fees:
					outstanding_amount=outstanding_amount+z["outstanding_amount"]
					for j in frappe.get_all("Fee Component",{"parent":z['name']},["fees_category",'outstanding_fees']):
						if j['fees_category']=="Re-Admission Fees":
							re_admission_fees=re_admission_fees+j['outstanding_fees']
						if j['fees_category']=="Arrear Dues":
							arrear_dues=arrear_dues+j['outstanding_fees']
						if j['fees_category']=="Tuition Fees":
							tuition_fees=tuition_fees+j['outstanding_fees']
						if j['fees_category']=="Development Fees":
							development_fees=development_fees+j['outstanding_fees']
						if j['fees_category']=="Hostel Admission Fees":
							hostel_admission_fees=hostel_admission_fees+j['outstanding_fees']
						if j['fees_category']=="Counselling Fees":
							counselling_fees=counselling_fees+j['outstanding_fees']
						if j['fees_category']=="Examination Fees":
							examination_fees=examination_fees+j['outstanding_fees']
						if j['fees_category']=="Transportation Fees":
							transportation_fees=transportation_fees+j['outstanding_fees']
						if j['fees_category']=="Mess Fees":
							mess_fees=mess_fees+j['outstanding_fees']
						if j['fees_category']=="Miscellaneous Fees":
							miscellaneous_fees=miscellaneous_fees+j['outstanding_fees']
						if j['fees_category']=="Hostel Fees":
							hostel_fees=hostel_fees+j['outstanding_fees']
						if j['fees_category']=="Other Institutional Fees":
							other_institutional_fees=other_institutional_fees+j['outstanding_fees']		
			for y in stud_payment_upload_1:
				if y["party"]==t:
					y['outstanding_amount']=outstanding_amount
					y['re_admission_fees']=re_admission_fees
					y['arrear_dues']=arrear_dues
					y['tuition_fees']=tuition_fees
					y['development_fees']=development_fees
					y['hostel_admission_fees']=hostel_admission_fees
					y['counselling_fees']=counselling_fees
					y['examination_fees']=examination_fees
					y['transportation_fees']=transportation_fees
					y['mess_fees']=mess_fees
					y['miscellaneous_fees']=miscellaneous_fees
					y['hostel_fees']=hostel_fees
					y['other_institutional_fees']=other_institutional_fees

					y['outstanding_amount_cal']=outstanding_amount
					y['re_admission_fees_cal']=re_admission_fees
					y['arrear_dues_cal']=arrear_dues
					y['tuition_fees_cal']=tuition_fees
					y['development_fees_cal']=development_fees
					y['hostel_admission_fees_cal']=hostel_admission_fees
					y['counselling_fees_cal']=counselling_fees
					y['examination_fees_cal']=examination_fees
					y['transportation_fees_cal']=transportation_fees
					y['mess_fees_cal']=mess_fees
					y['miscellaneous_fees_cal']=miscellaneous_fees
					y['hostel_fees_cal']=hostel_fees
					y['other_institutional_fees_cal']=other_institutional_fees
		stud_payment_upload=stud_payment_upload_1
	# print("\n\n\n")
	# print(stud_payment_upload)
	for t in stud_payment_upload:
		"""Reference"""
		############### structured fees
		fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",t['student']],["outstanding_amount","!=",0],
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

		paying_tuition_fees=0
		paying_development_fees=0
		paying_other_institutional_fees=0
		paying_miscellaneous_fees=0
		paying_examination_fees=0
		paying_transportation_fees=0
		paying_counselling_fees=0
		paying_re_admission_fees=0
		paying_arrear_dues=0
		paying_hostel_admission_fees=0
		paying_hostel_fees=0
		paying_mess_fees=0
		paying_fees_refundable__adjustable=0

		allocated_amount=t['amount']
		print("\n\n\n")
		print(allocated_amount)
		# {'name': 'ACC-PMD-2022-00006', 'student': 'EDU-STU-2022-00896', 'unique_transaction_reference_utr': 'aaccddee11', 
		# 'amount': 80000.0, 'remarks': None, 'reconciliation_status': 1, 'student_name': 'ASHISH KUMAR DAS', 'outstanding_amount': 191750.0, 're_admission_fees': 0, 
		# 'arrear_dues': 0, 'tuition_fees': 56850.0, 'development_fees': 15900.0, 'hostel_admission_fees': 0, 'counselling_fees': 0, 'examination_fees': 1400.0, 'transportation_fees': 0, 
		# 'mess_fees': 0, 'miscellaneous_fees': 0, 'hostel_fees': 0, 'other_institutional_fees': 117600.0, 'outstanding_amount_cal': 191750.0, 're_admission_fees_cal': 0, 'arrear_dues_cal': 0, 
		# 'tuition_fees_cal': 56850.0, 'development_fees_cal': 15900.0, 'hostel_admission_fees_cal': 0, 'counselling_fees_cal': 0, 'examination_fees_cal': 1400.0, 'transportation_fees_cal': 0, 
		# 'mess_fees_cal': 0, 'miscellaneous_fees_cal': 0, 'hostel_fees_cal': 0, 'other_institutional_fees_cal': 117600.0}

		for k in structured_fees:
			cal_fee=0
			if allocated_amount>0:
				##Tuition Fees
				if k['fees_category']=='Tuition Fees' and t['tuition_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['tuition_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['tuition_fees_cal']
						if fee_head_cal>0:
							t['tuition_fees_cal']=t['tuition_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_tuition_fees=paying_tuition_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['tuition_fees_cal']=t['tuition_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_tuition_fees=paying_tuition_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['tuition_fees_cal']
							t['tuition_fees_cal']=t['tuition_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_tuition_fees=paying_tuition_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['tuition_fees_cal']
						if fee_head_cal>0:
							t['tuition_fees_cal']=t['tuition_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_tuition_fees=paying_tuition_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['tuition_fees_cal']=t['tuition_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_tuition_fees=paying_tuition_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['tuition_fees_cal']
							t['tuition_fees_cal']=t['tuition_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_tuition_fees=paying_tuition_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['tuition_fees_cal']
						if fee_head_cal>0:
							t['tuition_fees_cal']=t['tuition_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_tuition_fees=paying_tuition_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['tuition_fees_cal']=t['tuition_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_tuition_fees=paying_tuition_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['tuition_fees_cal']
							t['tuition_fees_cal']=t['tuition_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_tuition_fees=paying_tuition_fees+reducing_amount
				
				##Development Fees 
				elif k['fees_category']=='Development Fees' and t['development_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['development_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['development_fees_cal']
						if fee_head_cal>0:
							t['development_fees_cal']=t['development_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_development_fees=paying_development_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['development_fees_cal']=t['development_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_development_fees=paying_development_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['development_fees_cal']
							t['development_fees_cal']=t['development_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_development_fees=paying_development_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['development_fees_cal']
						if fee_head_cal>0:
							t['development_fees_cal']=t['development_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_development_fees=paying_development_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['development_fees_cal']=t['development_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_development_fees=paying_development_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['development_fees_cal']
							t['development_fees_cal']=t['development_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_development_fees=paying_development_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['development_fees_cal']
						if fee_head_cal>0:
							t['development_fees_cal']=t['development_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_development_fees=paying_development_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['development_fees_cal']=t['development_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_development_fees=paying_development_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['development_fees_cal']
							t['development_fees_cal']=t['development_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_development_fees=paying_development_fees+reducing_amount

				##Re-Admission Fees
				elif k['fees_category']=='Re-Admission Fees' and t['re_admission_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['re_admission_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['re_admission_fees_cal']
						if fee_head_cal>0:
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_re_admission_fees=paying_re_admission_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_re_admission_fees=paying_re_admission_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['re_admission_fees_cal']
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_re_admission_fees=paying_re_admission_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['re_admission_fees_cal']
						if fee_head_cal>0:
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_re_admission_fees=paying_re_admission_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_re_admission_fees=paying_re_admission_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['re_admission_fees_cal']
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_re_admission_fees=paying_re_admission_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['re_admission_fees_cal']
						if fee_head_cal>0:
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_re_admission_fees=paying_re_admission_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_re_admission_fees=paying_re_admission_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['re_admission_fees_cal']
							t['re_admission_fees_cal']=t['re_admission_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_re_admission_fees=paying_re_admission_fees+reducing_amount

				##Arrear Dues
				elif k['fees_category']=='Arrear Dues' and t['arrear_dues_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['arrear_dues_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['arrear_dues_cal']
						if fee_head_cal>0:
							t['arrear_dues_cal']=t['arrear_dues_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_arrear_dues=paying_arrear_dues+k['outstanding_fees']
						elif fee_head_cal==0:
							t['arrear_dues_cal']=t['arrear_dues_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_arrear_dues=paying_arrear_dues+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['arrear_dues_cal']
							t['arrear_dues_cal']=t['arrear_dues_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_arrear_dues=paying_arrear_dues+reducing_amount
					elif cal_fee==0:
						if fee_head_cal>0:
							t['arrear_dues_cal']=t['arrear_dues_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_arrear_dues=paying_arrear_dues+k['outstanding_fees']
						elif fee_head_cal==0:
							t['arrear_dues_cal']=t['arrear_dues_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_arrear_dues=paying_arrear_dues+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['arrear_dues_cal']
							t['arrear_dues_cal']=t['arrear_dues_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_arrear_dues=paying_arrear_dues+reducing_amount
					elif cal_fee<0:
						if fee_head_cal>0:
							t['arrear_dues_cal']=t['arrear_dues_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_arrear_dues=paying_arrear_dues+k['outstanding_fees']
						elif fee_head_cal==0:
							t['arrear_dues_cal']=t['arrear_dues_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_arrear_dues=paying_arrear_dues+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['arrear_dues_cal']
							t['arrear_dues_cal']=t['arrear_dues_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_arrear_dues=paying_arrear_dues+reducing_amount
						
				##Hostel Admission Fees
				elif k['fees_category']=='Hostel Admission Fees' and t['hostel_admission_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['hostel_admission_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['hostel_admission_fees_cal']
						if fee_head_cal>0:
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_admission_fees=paying_hostel_admission_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_admission_fees=paying_hostel_admission_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['hostel_admission_fees_cal']
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_hostel_admission_fees=paying_hostel_admission_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['hostel_admission_fees_cal']
						if fee_head_cal>0:
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_admission_fees=paying_hostel_admission_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_admission_fees=paying_hostel_admission_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['hostel_admission_fees_cal']
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_hostel_admission_fees=paying_hostel_admission_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['hostel_admission_fees_cal']
						if fee_head_cal>0:
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_admission_fees=paying_hostel_admission_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_admission_fees=paying_hostel_admission_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['hostel_admission_fees_cal']
							t['hostel_admission_fees_cal']=t['hostel_admission_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_hostel_admission_fees=paying_hostel_admission_fees+reducing_amount

				##Counselling Fees
				elif k['fees_category']=='Counselling Fees' and t['counselling_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['counselling_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['counselling_fees_cal']
						if fee_head_cal>0:
							t['counselling_fees_cal']=t['counselling_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_counselling_fees=paying_counselling_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['counselling_fees_cal']=t['counselling_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_counselling_fees=paying_counselling_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['counselling_fees_cal']
							t['counselling_fees_cal']=t['counselling_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_counselling_fees=paying_counselling_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['counselling_fees_cal']
						if fee_head_cal>0:
							t['counselling_fees_cal']=t['counselling_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_counselling_fees=paying_counselling_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['counselling_fees_cal']=t['counselling_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_counselling_fees=paying_counselling_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['counselling_fees_cal']
							t['counselling_fees_cal']=t['counselling_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_counselling_fees=paying_counselling_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['counselling_fees_cal']
						if fee_head_cal>0:
							t['counselling_fees_cal']=t['counselling_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_counselling_fees=paying_counselling_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['counselling_fees_cal']=t['counselling_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_counselling_fees=paying_counselling_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['counselling_fees_cal']
							t['counselling_fees_cal']=t['counselling_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_counselling_fees=paying_counselling_fees+reducing_amount
						
				##Examination Fees
				elif k['fees_category']=='Examination Fees' and t['examination_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['examination_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['examination_fees_cal']
						if fee_head_cal>0:
							t['examination_fees_cal']=t['examination_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_examination_fees=paying_examination_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['examination_fees_cal']=t['examination_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_examination_fees=paying_examination_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['examination_fees_cal']
							t['examination_fees_cal']=t['examination_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_examination_fees=paying_examination_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['examination_fees_cal']
						if fee_head_cal>0:
							t['examination_fees_cal']=t['examination_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_examination_fees=paying_examination_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['examination_fees_cal']=t['examination_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_examination_fees=paying_examination_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['examination_fees_cal']
							t['examination_fees_cal']=t['examination_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_examination_fees=paying_examination_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['examination_fees_cal']
						if fee_head_cal>0:
							t['examination_fees_cal']=t['examination_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_examination_fees=paying_examination_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['examination_fees_cal']=t['examination_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_examination_fees=paying_examination_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['examination_fees_cal']
							t['examination_fees_cal']=t['examination_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_examination_fees=paying_examination_fees+reducing_amount

				##Transportation Fees
				elif k['fees_category']=='Transportation Fees' and t['transportation_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['transportation_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['transportation_fees_cal']
						if fee_head_cal>0:
							t['transportation_fees_cal']=t['transportation_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_transportation_fees=paying_transportation_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['transportation_fees_cal']=t['transportation_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_transportation_fees=paying_transportation_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['transportation_fees_cal']
							t['transportation_fees_cal']=t['transportation_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_transportation_fees=paying_transportation_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['transportation_fees_cal']
						if fee_head_cal>0:
							t['transportation_fees_cal']=t['transportation_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_transportation_fees=paying_transportation_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['transportation_fees_cal']=t['transportation_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_transportation_fees=paying_transportation_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['transportation_fees_cal']
							t['transportation_fees_cal']=t['transportation_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_transportation_fees=paying_transportation_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['transportation_fees_cal']
						if fee_head_cal>0:
							t['transportation_fees_cal']=t['transportation_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_transportation_fees=paying_transportation_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['transportation_fees_cal']=t['transportation_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_transportation_fees=paying_transportation_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['transportation_fees_cal']
							t['transportation_fees_cal']=t['transportation_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_transportation_fees=paying_transportation_fees+reducing_amount

				##Mess Fees
				elif k['fees_category']=='Mess Fees' and t['mess_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['mess_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['mess_fees_cal']
						if fee_head_cal>0:
							t['mess_fees_cal']=t['mess_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_mess_fees=paying_mess_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['mess_fees_cal']=t['mess_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_mess_fees=paying_mess_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['mess_fees_cal']
							t['mess_fees_cal']=t['mess_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_mess_fees=paying_mess_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['mess_fees_cal']
						if fee_head_cal>0:
							t['mess_fees_cal']=t['mess_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_mess_fees=paying_mess_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['mess_fees_cal']=t['mess_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_mess_fees=paying_mess_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['mess_fees_cal']
							t['mess_fees_cal']=t['mess_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_mess_fees=paying_mess_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['mess_fees_cal']
						if fee_head_cal>0:
							t['mess_fees_cal']=t['mess_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_mess_fees=paying_mess_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['mess_fees_cal']=t['mess_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_mess_fees=paying_mess_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['mess_fees_cal']
							t['mess_fees_cal']=t['mess_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_mess_fees=paying_mess_fees+reducing_amount

				##Miscellaneous Fees
				elif k['fees_category']=='Miscellaneous Fees' and t['miscellaneous_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['miscellaneous_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['miscellaneous_fees_cal']
						if fee_head_cal>0:
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_miscellaneous_fees=paying_miscellaneous_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_miscellaneous_fees=paying_miscellaneous_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['miscellaneous_fees_cal']
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_miscellaneous_fees=paying_miscellaneous_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['miscellaneous_fees_cal']
						if fee_head_cal>0:
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_miscellaneous_fees=paying_miscellaneous_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_miscellaneous_fees=paying_miscellaneous_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['miscellaneous_fees_cal']
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_miscellaneous_fees=paying_miscellaneous_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['miscellaneous_fees_cal']
						if fee_head_cal>0:
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_miscellaneous_fees=paying_miscellaneous_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_miscellaneous_fees=paying_miscellaneous_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['miscellaneous_fees_cal']
							t['miscellaneous_fees_cal']=t['miscellaneous_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_miscellaneous_fees=paying_miscellaneous_fees+reducing_amount

				##Hostel Fees
				elif k['fees_category']=='Hostel Fees' and t['hostel_fees_cal']>0 and k['outstanding_fees']>0:
					cal_fee=allocated_amount-t['hostel_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['hostel_fees_cal']
						if fee_head_cal>0:
							t['hostel_fees_cal']=t['hostel_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_fees=paying_hostel_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['hostel_fees_cal']=t['hostel_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_fees=paying_hostel_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['hostel_fees_cal']
							t['hostel_fees_cal']=t['hostel_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_hostel_fees=paying_hostel_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['hostel_fees_cal']
						if fee_head_cal>0:
							t['hostel_fees_cal']=t['hostel_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_fees=paying_hostel_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['hostel_fees_cal']=t['hostel_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_fees=paying_hostel_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['hostel_fees_cal']
							t['hostel_fees_cal']=t['hostel_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_hostel_fees=paying_hostel_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=k['outstanding_fees']-t['hostel_fees_cal']
						if fee_head_cal>0:
							t['hostel_fees_cal']=t['hostel_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_fees=paying_hostel_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['hostel_fees_cal']=t['hostel_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_hostel_fees=paying_hostel_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['hostel_fees_cal']
							t['hostel_fees_cal']=t['hostel_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_hostel_fees=paying_hostel_fees+reducing_amount

				##Other Institutional Fees
				elif k['fees_category']=='Other Institutional Fees' and t['other_institutional_fees_cal']>0 and k['outstanding_fees']>0:
					print("\n\n\n")
					cal_fee=allocated_amount-t['other_institutional_fees_cal']
					if cal_fee>0:
						fee_head_cal=k['outstanding_fees']-t['other_institutional_fees_cal']
						if fee_head_cal>0:
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_other_institutional_fees=paying_other_institutional_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_other_institutional_fees=paying_other_institutional_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['other_institutional_fees_cal']
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_other_institutional_fees=paying_other_institutional_fees+reducing_amount
					elif cal_fee==0:
						fee_head_cal=k['outstanding_fees']-t['other_institutional_fees_cal']
						if fee_head_cal>0:
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_other_institutional_fees=paying_other_institutional_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_other_institutional_fees=paying_other_institutional_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=t['other_institutional_fees_cal']
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_other_institutional_fees=paying_other_institutional_fees+reducing_amount
					elif cal_fee<0:
						fee_head_cal=allocated_amount-t['other_institutional_fees_cal']
						if fee_head_cal>0:
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_other_institutional_fees=paying_other_institutional_fees+k['outstanding_fees']
						elif fee_head_cal==0:
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-k['outstanding_fees']
							allocated_amount=allocated_amount-k['outstanding_fees']
							paying_other_institutional_fees=paying_other_institutional_fees+k['outstanding_fees']
						elif fee_head_cal<0:
							reducing_amount=allocated_amount
							t['other_institutional_fees_cal']=t['other_institutional_fees_cal']-reducing_amount
							allocated_amount=allocated_amount-reducing_amount
							paying_other_institutional_fees=paying_other_institutional_fees+reducing_amount
				
				##Fees Refundable / Adjustable
				else:
					paying_fees_refundable__adjustable=allocated_amount

		t['paying_re_admission_fees']=paying_re_admission_fees
		t['paying_arrear_dues']=paying_arrear_dues
		t['paying_tuition_fees']=paying_tuition_fees
		t['paying_development_fees']=paying_development_fees
		t['paying_hostel_admission_fees']=paying_hostel_admission_fees
		t['paying_counselling_fees']=paying_counselling_fees
		t['paying_examination_fees']=paying_examination_fees
		t['paying_transportation_fees']=paying_transportation_fees
		t['paying_mess_fees']=paying_mess_fees
		t['paying_miscellaneous_fees']=paying_miscellaneous_fees
		t['paying_hostel_fees']=paying_hostel_fees
		t['paying_other_institutional_fees']=paying_other_institutional_fees
		t['paying_fees_refundable__adjustable']=paying_fees_refundable__adjustable

	# print(stud_payment_upload)
	return stud_payment_upload
