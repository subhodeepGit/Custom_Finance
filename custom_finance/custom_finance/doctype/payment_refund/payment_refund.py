# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaymentRefund(Document):
		def on_submit(self):
			je = frappe.new_doc("Journal Entry")
			je.posting_date = self.posting_date
			ref_details = frappe.get_all("Payment Refund",{"name":self.name},['party_type','party','paid_from','cost_center','paid_from_account_currency'])
			ref_details_cd = frappe.get_all("Payment Entry Reference Refund",filters={"parent":self.name},fields=['account_paid_from','total_amount'])
			################################Cash Entry###################################
			je.append("accounts",{
					'account' : ref_details[0]['paid_from'],
					'party_type' : ref_details[0]['party_type'],
					'party' : ref_details[0]['party'],
					'credit_in_account_currency' : ref_details_cd[0]['total_amount'],
					'cost_center' : ref_details[0]['cost_center'],
					'account_currency': ref_details[0]['paid_from_account_currency']
				})
			#################################Refundable Entry##############################
			je.append("accounts",{
					'account' : ref_details_cd[0]['account_paid_from'],
					'party_type' : ref_details[0]['party_type'],
					'party' : ref_details[0]['party'],
					'debit_in_account_currency' : ref_details_cd[0]['total_amount'],
					'cost_center' : ref_details[0]['cost_center'],
					'account_currency': ref_details[0]['paid_from_account_currency']
				})
			je.save()
			je.submit()

@frappe.whitelist()
def paid_from_fetch(mode_of_payment,company):
	mode_of_payment=frappe.get_all("Mode of Payment Account",{"parent":mode_of_payment,'company': company},['name','company','default_account'])
	if len(mode_of_payment)==0:
		frappe.throw("Account not maintained in Mode of Payment")
	else:
		return mode_of_payment[0]['default_account']	