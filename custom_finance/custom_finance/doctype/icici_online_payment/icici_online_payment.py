# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ICICIOnlinePayment(Document):
	pass
	def on_cancel(self):
		frappe.throw("Once form is submited it can't be canceled")


@frappe.whitelist()
def get_outstanding_amount(student):
	fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",student],["outstanding_amount","!=",0],["docstatus","=",1]],
															fields=['outstanding_amount'],
															order_by="due_date asc")
	outstanding_amount=0
	for t in fee_voucher_list:
		outstanding_amount=t['outstanding_amount']+outstanding_amount
	return outstanding_amount