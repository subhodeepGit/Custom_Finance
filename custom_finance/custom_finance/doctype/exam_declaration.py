from __future__ import unicode_literals
from re import split
import frappe,json
from frappe.model.document import Document
from datetime import datetime
from frappe.utils.background_jobs import enqueue
from kp_edtec.ed_tec.utils import date_greater_than_or_equal,academic_term,semester_belongs_to_programs,get_courses_by_semester,duplicate_row_validation
from frappe.utils import flt
from kp_edtec.ed_tec.notification.custom_notification import exam_declaration_submit,exam_declaration_for_instructor_submit
from kp_edtec.ed_tec.doctype.user_permission import add_user_permission
from pytz import all_timezones, country_names
from frappe.utils.data import nowtime
from frappe.utils import cint, flt, cstr
from frappe import _

def on_submit(self,method):
    make_exam_assessment_result(self)

def on_cancel(self,method):
    cancel_fees(self)
# creation of fee(as tool)
@frappe.whitelist()
def make_exam_assessment_result(self):
    self.db_set("certificate_creation_status", "In Process")
    frappe.publish_realtime("exam_declaration_progress",
        {"progress": "0", "reload": 1}, user=frappe.session.user)

    total_records = len(self.get("students"))
    if total_records > 35:
        frappe.msgprint(_(''' Records will be created in the background.
            In case of any error the error message will be updated in the Schedule.'''))
        enqueue(create_conduct_certificate, queue='default', timeout=6000, event='create_conduct_certificate',
            exam_declaration=self.name)

    else:
        create_conduct_certificate(self.name)
            
def create_conduct_certificate(exam_declaration):
    doc = frappe.get_doc("Exam Declaration", exam_declaration)
    error = False
    total_records = len(doc.get("students"))
    created_records = 0
    if not total_records:
        frappe.throw(_("Please setup Students under Student Groups"))
    for d in doc.get("students"):
        # try:
        result=frappe.new_doc("Fees")
        result.student=d.student
        result.student_name=d.student_name
        result.roll_no=d.roll_no
        result.registration_number=d.registration_number
        for enroll in frappe.get_all("Program Enrollment",{"student":d.student,"docstatus":1,"academic_term":doc.academic_term},['programs','program','academic_term','academic_year'],order_by="creation desc",limit=1):
            result.programs=enroll.programs
            result.program=enroll.program
            result.program_enrollment=enroll.name
        for fee_stu in doc.get("fee_structure"):
            result.fee_structure=fee_stu.fee_structure
            print(fee_stu.fee_structure)
            result.due_date=fee_stu.due_date
            ref_details = frappe.get_all("Fee Component",{"parent":fee_stu.fee_structure},['fees_category','amount','receivable_account','income_account','company','grand_fee_amount','outstanding_fees'])
            for i in ref_details:
                result.append("components",{
                        'fees_category' : i['fees_category'],
                        'amount' : i['amount'],
                        'receivable_account' : i['receivable_account'],
                        'income_account' : i['income_account'],
                        'company' : i['company'],
                        'grand_fee_amount' : i['grand_fee_amount'],
                        'outstanding_fees' : i['outstanding_fees'],
                    })

            
        result.academic_year=doc.academic_year
        result.academic_term=doc.academic_term
            
        result.submit()
        created_records += 1
    frappe.msgprint("Record Created")    
#list append/fetching data from child doctype/cancel doctype
def cancel_fees(self):
    student=[]
    fee_structure_id=[]
    for t in self.get("students"):
        student.append(t.student)
    for t in self.get("fee_structure"): 
        fee_structure_id.append(t.fee_structure)   
    voucher_no=[]    
    for t in fee_structure_id:
        for j in student:
            fee_id=frappe.get_all("Fees",{"student":j,"fee_structure":t},['name'])
            voucher_no.append(fee_id[0]['name'])
    for t in voucher_no:
        cancel_doc = frappe.get_doc("Fees",t)
        cancel_doc.cancel()      
    

	

     