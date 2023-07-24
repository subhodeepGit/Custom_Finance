# Copyright (c) 2023, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaymentDishonor(Document):
	def on_submit(doc):
		cancel_payment_entry(doc,doc.payment_entry)
		
	def on_cancel(doc):
		# doc = frappe.get_doc('Payment Entry', doc.payment_entry)
		frappe.db.set_value('Payment Entry', doc.payment_entry, 'payment_status', "")
		frappe.db.set_value('Payment Entry', doc.payment_entry, 'payment_dishonour', "")
		# doc.payment_status=""
		# doc.payment_dishonour=""
		# doc.reload()


def cancel_payment_entry(doc,voucher_no):
	cancel_doc = frappe.get_doc("Payment Entry",voucher_no)
	cancel_doc.cancel()
	frappe.db.set_value('Payment Entry', voucher_no, 'payment_status', 'Dishonoured')
	frappe.db.set_value('Payment Entry', voucher_no, 'payment_dishonour', doc.name)
	# frappe.db.set_value('Payment Entry', voucher_no, 'docstatus', '3')

@frappe.whitelist()
def get_payment_entry_child(payment_entry):
	if payment_entry:
		payment_entry_child = frappe.get_all("Payment Entry Reference", fields=["reference_doctype", "fees_category", "semester","program","account_paid_from","description","fee_structure","hostel_fee_structure","account_paid_to","reference_name","due_date","total_amount","outstanding_amount","allocated_amount"] ,filters={"parent": payment_entry}, order_by= "idx asc")
		return payment_entry_child
	
@frappe.whitelist()
def get_payment_entry_record(student):
	payment_entry = frappe.get_all('Payment Entry' ,{'party':student,'docstatus':1}, ['name'])	
	return payment_entry

@frappe.whitelist()
def get_payment_entry(payment_entry):
		if payment_entry:
			payment_entry = frappe.get_all('Payment Entry' ,{'name':payment_entry,'docstatus':1}, ["posting_date","company","mode_of_payment","student","party_name","roll_no","sams_portal_id","permanent_registration_number","student_email","paid_amount"])	
			return payment_entry
		
