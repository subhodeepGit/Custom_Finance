# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

from dataclasses import fields
import frappe
from frappe.model.document import Document

class AutoReconciliation(Document):
	pass


@frappe.whitelist()
def get_fees(date=None,type_of_transaction=None):
	print("\n\n\n\n\n")
	stud_payment_upload=frappe.get_all("Payment Details Upload",filters=[["date_of_transaction","=",date],['type_of_transaction','=',type_of_transaction],
											["reconciliation_status","=",1],["reconciliation_status","=",1],["payment_status","=",0]],
											fields=['name','student','unique_transaction_reference_utr','amount',"remarks","reconciliation_status", "student_name"])
	stu_info=[]
	for t in stud_payment_upload:
		stu_info.append(t['student'])										
	stu_info = list(set(stu_info))

	# for t in stu_info:
	# 	fees=frappe.get_all("Fees",filters=[["student","=",t],['']])
	# 	print(t)
	return stud_payment_upload										