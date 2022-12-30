# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date 
import pandas as pd

class PaymentDetailsUpload(Document):
	def validate(self):
		validate_urt(self)
		today = date.today()
		date_of_transaction=pd.to_datetime(pd.to_datetime(self.date_of_transaction).date())
		if date_of_transaction<=today:
			pass
		else:
			frappe.throw("Posting date can't in future")
		# self.set_value()
		if not self.get("__islocal"):
			set_user_permission(self)	
	def on_submit(self):
		brs_info=frappe.db.get_all("Bank Reconciliation Statement",{'docstatus':1,'unique_transaction_reference_utr':self.unique_transaction_reference_utr},['name','amount','date','type_of_transaction'])
		if not brs_info:
			self.reconciliation_status=0
		else:
			if self.amount==brs_info[0]['amount']:	
				self.reconciliation_status=1
				self.brs_name=brs_info[0]['name']
				self.date_of_transaction=brs_info[0]['date']
				# self.type_of_transaction=brs_info[0]['type_of_transaction']
				frappe.db.set_value("Payment Details Upload",self.name,'reconciliation_status',1)
				frappe.db.set_value("Payment Details Upload",self.name,'brs_name',brs_info[0]['name'])
				
				

			else:
				self.reconciliation_status=0
				self.brs_name=''
				frappe.db.set_value("Payment Details Upload",self.name,'reconciliation_status',0)
				frappe.db.set_value("Payment Details Upload",self.name,'brs_name','')
				frappe.msgprint("paid amount does not match with Bank Data")
		
		pay_info=frappe.db.get_all("Bank Reconciliation Statement",{'docstatus':1,'unique_transaction_reference_utr':self.unique_transaction_reference_utr},['name','amount','unique_transaction_reference_utr'])	
		if len(pay_info)>0:															
			if pay_info[0]['amount']==self.amount or pay_info[0]['unique_transaction_reference_utr']==self.unique_transaction_reference_utr:
				frappe.db.set_value("Bank Reconciliation Statement",pay_info[0]['name'],'type_of_transaction',self.type_of_transaction)	
				
	# def set_value(self):	
	# 	pay_info=frappe.db.get_all("Bank Reconciliation Statement",{'docstatus':1,'unique_transaction_reference_utr':'self.unique_transaction_reference_utr'},['name','amount'])	
	# 	if len(pay_info)>0:															
	# 		if pay_info[0]['amount']==self.amount:
	# 			frappe.db.set_value("Payment Details Upload",pay_info[0]['name'],'type_of_transaction',self.type_of_transaction)	
		
		frappe.msgprint("Please Wait for 24 hr-48 hr for Money Receipt. Money Receipt will be sent to your mail.")
	def on_cancel(self):
		if self.payment_status==1:
			frappe.throw("Payment status Updated for the UTR no. So it can't be canceled")			

@frappe.whitelist()
def utr_callback(party=None, mode_of_payment=None):
	get_utr=frappe.get_all("Payment Details Upload",{"student":party,"docstatus":1,"payment_status":0,"reconciliation_status":1,"type_of_transaction":mode_of_payment},['unique_transaction_reference_utr'])
	if len(get_utr)!=0:
		return get_utr[0]['unique_transaction_reference_utr']
	else:
		return ''	

def validate_urt(self):
	data=frappe.get_all("Payment Details Upload",{"unique_transaction_reference_utr":self.unique_transaction_reference_utr,"docstatus":1})
	if len(data)!=0:
		frappe.throw("UTR should be Unique")

def set_user_permission(self):
    for stu in frappe.get_all("Student",{"name":self.student},['student_email_id']):
        add_user_permission("Payment Details Upload",self.name, stu.student_email_id, self)

def add_user_permission(doctype, name, user,ref, ignore_permissions=True, applicable_for=None,is_default=0, hide_descendants=0, apply_to_all_doctypes=1):
	'''Add user permission'''
	from frappe.core.doctype.user_permission.user_permission import user_permission_exists

	if not user_permission_exists(user, doctype, name, applicable_for):
		if not frappe.db.exists(doctype, name):
			frappe.throw(_("{0} {1} not found").format(_(doctype), name), frappe.DoesNotExistError)

		frappe.get_doc(dict(
			doctype='User Permission',
			user=user,
			allow=doctype,
			for_value=name,
			is_default=is_default,
			applicable_for=applicable_for,
			hide_descendants=hide_descendants,
			reference_doctype=ref.get("doctype"),
			reference_docname=ref.get("name"),
			apply_to_all_doctypes = apply_to_all_doctypes
		)).insert(ignore_permissions=ignore_permissions)