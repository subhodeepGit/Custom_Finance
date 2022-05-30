# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BankReconciliationStatement(Document):
	def validate(doc):
		doc.total_allocated_amount=doc.amount
	def on_submit(doc):
		st_payment_upload=frappe.db.get_all("Payment Details Upload",{'docstatus':1,'unique_transaction_reference_utr':doc.unique_transaction_reference_utr,
																	"type_of_transaction":doc.type_of_transaction},['name','amount'])
		if st_payment_upload[0]['amount']==doc.amount:
			frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'reconciliation_status',1)
			frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'brs_name',doc.name)
			frappe.db.set_value("Payment Details Upload",st_payment_upload[0]['name'],'date_of_transaction',doc.date)
		else:
			frappe.msgprint("Not Reconciled But data saved")	
