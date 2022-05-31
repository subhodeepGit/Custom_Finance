# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date 
import pandas as pd

class PaymentDetailsUpload(Document):
	def validate(self):
		today = date.today()
		date_of_transaction=pd.to_datetime(pd.to_datetime(self.date_of_transaction).date())
		if date_of_transaction<=today:
			pass
		else:
			frappe.throw("Posting date can't in future")
	def on_submit(self):
		brs_info=frappe.db.get_all("Bank Reconciliation Statement",{'docstatus':1,'unique_transaction_reference_utr':self.unique_transaction_reference_utr,
																	"type_of_transaction":self.type_of_transaction},['name','amount','date'])
		if not brs_info:
			self.reconciliation_status=0
		else:
			if self.amount==brs_info[0]['amount']:	
				self.reconciliation_status=1
				self.brs_name=brs_info[0]['name']
				self.date_of_transaction=brs_info[0]['date']
				frappe.db.set_value("Payment Details Upload",self.name,'reconciliation_status',1)
				frappe.db.set_value("Payment Details Upload",self.name,'brs_name',brs_info[0]['name'])
				frappe.db.set_value("Payment Details Upload",self.name,'date_of_transaction',brs_info[0]['date'])
			else:
				self.reconciliation_status=0
				self.brs_name=''
				frappe.db.set_value("Payment Details Upload",self.name,'reconciliation_status',0)
				frappe.db.set_value("Payment Details Upload",self.name,'brs_name','')
				frappe.msgprint("paid amount does not match with Bank Data")
	def on_cancel(self):
		if self.payment_status==1:
			frappe.throw("Payment status Updated for the UTR no. So it can't be canceled")			

@frappe.whitelist()
def utr_callback(party, mode_of_payment):
	get_utr=frappe.get_all("Payment Details Upload",{"student":party,"docstatus":1,"payment_status":0,"reconciliation_status":1,"type_of_transaction":mode_of_payment},['unique_transaction_reference_utr'])
	if len(get_utr)!=0:
		return get_utr[0]['unique_transaction_reference_utr']
	else:
		return ''	

