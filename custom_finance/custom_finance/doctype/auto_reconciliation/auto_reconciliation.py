# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AutoReconciliation(Document):
	pass


@frappe.whitelist()
def get_fees(date,type_of_transaction):
	print("\n\n\n\n\n")
	stud_payment_upload=frappe.get_all("Payment Details Upload",fields=[["date_of_transaction","=",date],
											["reconciliation_status","=",1],["reconciliation_status","=",1],["payment_status","=",0]])