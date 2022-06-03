# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaymentRefund(Document):
		pass

@frappe.whitelist()
def paid_from_fetch(mode_of_payment,company):
	mode_of_payment=frappe.get_all("Mode of Payment Account",{"parent":mode_of_payment,'company': company},['name','company','default_account'])
	if len(mode_of_payment)==0:
		frappe.throw("Account not maintained in Mode of Payment")
	else:
		return mode_of_payment[0]['default_account']	


