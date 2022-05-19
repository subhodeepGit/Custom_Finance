# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.education.api import enroll_student
from frappe.utils import cint, cstr
from frappe.utils.background_jobs import enqueue

class StudentReregistrationToolFees(Document):
    def onload(self):
        academic_term_reqd = cint(frappe.db.get_single_value('Education Settings', 'academic_term_reqd'))
        self.set_onload("academic_term_reqd", academic_term_reqd)

    @frappe.whitelist()
    def get_students(self):
        students = []
        if not self.program:
            frappe.throw(_("Mandatory field - Program"))
        elif not self.academic_year:
            frappe.throw(_("Mandatory field - Academic Year"))
        else:
            condition = 'and academic_term=%(academic_term)s' if self.academic_term else " "
            self.get_students_from = "Program Enrollment"
            condition2 = 'and student_batch_name=%(student_batch)s' if self.student_batch else " "
            students = frappe.db.sql('''select student, student_name, student_batch_name, roll_no,permanant_registration_number, student_category from `tabProgram Enrollment`
                where program=%(program)s and academic_year=%(academic_year)s {0} {1} and docstatus != 2'''
                .format(condition, condition2), self.as_dict(), as_dict=1)          

            student_list = [d.student for d in students]
            if student_list:
                inactive_students = frappe.db.sql('''
                    select name as student, title as student_name from `tabStudent` where name in (%s) and enabled = 0''' %
                    ', '.join(['%s']*len(student_list)), tuple(student_list), as_dict=1)

                for student in students:
                    if student.student in [d.student for d in inactive_students]:
                        students.remove(student)

        if students:
            return students
        else:
            frappe.throw(_("No students Found"))

    @frappe.whitelist()
    def enroll_students(self):
        # self.db_set("fee_creation_status", "In Process")
        # fee_structure_validation(self,validate=1)
        # existed_enrollment = [p.get('student') for p in frappe.db.get_list("Program Enrollment", {'student':['in', [s.student for s in self.students]],'programs':self.programs, 'program': self.new_semester,'academic_year':self.new_academic_year, 'academic_term':self.new_academic_term,'docstatus':1 }, 'student')]
        # if len(existed_enrollment) > 0:
        #     frappe.msgprint(_("{0} Students already enrolled").format( ', '.join(map(str, existed_enrollment))))
            
        # frappe.publish_realtime("student_reregistration_tool_fees",
		# 	{"progress": "0", "reload": 1}, user=frappe.session.user)
        total = len(self.students)
        if total > 10:
            frappe.msgprint(_('''Student Re-registration will be created in the background.
						In case of any error the error message will be updated in the Schedule.'''))
            enqueue(enroll_stud, queue='default', timeout=6000, event='enroll_stud',self=self)
        else:
            enroll_stud(self)

def enroll_stud(self):
    fee_structure_id=fee_structure_validation(self)
    total = len(self.students)
    existed_enrollment = [p.get('student') for p in frappe.db.get_list("Program Enrollment", {'student':['in', [s.student for s in self.students]],'programs':self.programs, 'program': self.new_semester,'academic_year':self.new_academic_year, 'academic_term':self.new_academic_term,'docstatus':1 }, 'student')]
    if len(existed_enrollment) > 0:
        frappe.msgprint(_("{0} Students already enrolled").format( ', '.join(map(str, existed_enrollment))))
    enrolled_students = []
    for i, stud in enumerate(self.students):
        frappe.publish_realtime("student_reregistration_tool_fees", dict(progress=[i+1, total]),{"reload": 1}, user=frappe.session.user)
        if stud.student and stud.student not in existed_enrollment:
            try:
                prog_enrollment = frappe.new_doc("Program Enrollment")
                prog_enrollment.student = stud.student
                prog_enrollment.student_name = stud.student_name
                prog_enrollment.programs = self.programs
                prog_enrollment.program = self.new_semester
                prog_enrollment.academic_year = self.new_academic_year
                prog_enrollment.academic_term = self.new_academic_term
                prog_enrollment.is_provisional_admission="No"
                prog_enrollment.admission_status="Admitted"
                prog_enrollment.student_batch_name = stud.student_batch_name if stud.student_batch_name else self.new_student_batch
                if stud.additional_course_1:
                    course_data  = frappe.db.get_value("Course",{'name':stud.additional_course_1},["course_name", "course_code"], as_dict=1)
                    if course_data:
                        course_data = course_data
                        create_course_row(prog_enrollment,stud.additional_course_1,course_data.course_name,course_data.course_code)
                for c in self.courses:
                    create_course_row(prog_enrollment,c.course,c.course_name,c.course_code)
                for pe in frappe.get_all("Program Enrollment",filters={"student":stud.student},order_by='`creation` DESC',limit=1):
                    prog_enrollment.reference_doctype="Program Enrollment"
                    prog_enrollment.reference_name=pe.name
                prog_enrollment.save()
                prog_enrollment.submit()
                create_fees(self,stud,fee_structure_id)
                enrolled_students.append(stud.student)
                # create_fees(self,stud,fee_structure_id,prog_enrollment.name)
            except Exception as e:
                error = True
                err_msg = frappe.local.message_log and "\n\n".join(frappe.local.message_log) or cstr(e)   

    frappe.msgprint(_("{0} Students have been enrolled").format(', '.join(map(str, enrolled_students))))
 
def create_course_row(prog_enrollment,course,course_name,course_code): 
    prog_enrollment.append("courses",{
        "course":course,
        "course_name":course_name,
        "course_code":course_code
    })

@frappe.whitelist()
def get_optional_courses(doctype, txt, searchfield, start, page_len, filters):
    course_list = []
    if filters.get('additional_course_1'):
        course_list.append(filters.get('additional_course_1'))
    if filters.get('additional_course_2'):
        course_list.append(filters.get('additional_course_2'))
    if filters.get('additional_course_3'):
        course_list.append(filters.get('additional_course_3'))
    return [[c.course, c.course_name] for c in frappe.db.get_list("Program Course",{"parent":filters.get("new_semester"),"required":0, 'course':['not in', course_list],'course_name':['like', '%{}%'.format(txt)]},['course','course_name'])]

def fee_structure_validation(self,validate=None): #KP
    existed_fs = frappe.db.get_list("Fee Structure", {'programs':self.programs, 'program':self.new_semester, 'fee_type':'Semester Fees', 'academic_year':self.new_academic_year, 'academic_term':self.new_academic_term, 'docstatus':1})
    if len(existed_fs) != 0 and validate== None:
        fee_structure_id = existed_fs[0]['name']
        return fee_structure_id
    elif len(existed_fs) != 0 and validate== 1:
        pass
    else:
        frappe.throw("Fee Structure Not Found")
    term_date = frappe.get_all("Academic Term",{'name': self.new_academic_term},['term_start_date','term_end_date'])
    if term_date == None:
        frappe.throw("Academic Term Start Date End Date Not Found")

def create_fees(self,stud,fee_structure_id): #KP
    # fees_info=frappe.get_list("Fees",filters=[['Program Enrollment','=',prog_enrollment]])
    # if len(fees_info)==0:
    data = frappe.get_all("Program Enrollment",{'student':stud.student,'docstatus':1},['name','program','programs','student_batch_name'],limit=1)
    term_date = frappe.get_all("Academic Term",{'name': self.new_academic_term},['term_start_date','term_end_date'])
    fee = frappe.new_doc("Fees")
    fee.student = stud.student
    fee.valid_from = term_date[0]['term_start_date']
    fee.valid_to = term_date[0]['term_end_date']
    fee.due_date = self.fees_due_date
    fee.program_enrollment = data[0]['name']
    fee.program = data[0]['program']
    fee.programs = data[0]['programs']
    fee.student_batch = data[0]['student_batch_name']
    fee.fee_structure = fee_structure_id
    ref_details = frappe.get_all("Fee Component",{"parent":fee_structure_id},['fees_category','amount','receivable_account','income_account','company','grand_fee_amount','outstanding_fees'])
    for i in ref_details:
        fee.append("components",{
            'fees_category' : i['fees_category'],
            'amount' : i['amount'],
            'receivable_account' : i['receivable_account'],
            'income_account' : i['income_account'],
            'company' : i['company'],
            'grand_fee_amount' : i['grand_fee_amount'],
            'outstanding_fees' : i['outstanding_fees'],
        })
    fee.save()
    fee.submit()