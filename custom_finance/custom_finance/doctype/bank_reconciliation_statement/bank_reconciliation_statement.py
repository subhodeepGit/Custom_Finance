# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class BankReconciliationStatement(Document):
	def validate(doc):
		doc.total_allocated_amount=doc.amount
