# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BankReconciliationStatement(Document):
	def validate(doc):
		urt_varification(doc)
		doc.total_allocated_amount=doc.amount
	def on_submit(doc):
		st_payment_upload=frappe.db.get_all("Payment Details Upload",{'docstatus':1,'unique_transaction_reference_utr':doc.unique_transaction_reference_utr},['name','amount'])
		if len(st_payment_upload)>0:															
			if st_payment_upload[0]['amount']==doc.amount:
				frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'reconciliation_status',1)
				frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'type_of_transaction',doc.type_of_transaction)
				frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'brs_name',doc.name)
				frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'date_of_transaction',doc.date)
			else:
				frappe.msgprint("Not Reconciled But data saved")	
	def on_cancel(doc):
		st_payment_upload=frappe.db.get_all("Payment Details Upload",{'docstatus':1,'unique_transaction_reference_utr':doc.unique_transaction_reference_utr,
																	"type_of_transaction":doc.type_of_transaction},['name','amount','payment_status'])
		if len(st_payment_upload)>0:
			if st_payment_upload[0]['payment_status']==0:														
				if st_payment_upload[0]['amount']==doc.amount:
					frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'reconciliation_status',0)
					frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'brs_name','')
			else:
				frappe.throw("Payment status Updated for the UTR no. So it can't be canceled")	
		if doc.total_allocated_amount==0:
			frappe.throw("Payment status Updated for the UTR no. So it can't be canceled")	

def urt_varification(doc):
	utr_data=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":doc.unique_transaction_reference_utr,"docstatus":1})
	if utr_data:
		frappe.throw("Urt Should be unique")																	