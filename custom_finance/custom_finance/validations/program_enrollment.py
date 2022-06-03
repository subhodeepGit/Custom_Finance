import frappe
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from ed_tec.ed_tec.doctype.user_permission import add_user_permission,delete_ref_doctype_permissions


#program enrollment done whether FS is there or not
#Semester fees added
#Cancel functionality added without FS ID
#check date mandatory in backend.

def validate(doc,method):                           
    fee_structure_id = fee_structure_validation(doc)

def on_cancel(doc,method):
    fee_structure_id = get_fee_structure(doc)

    if len(fee_structure_id)!=0:
        cancel_fees(doc,fee_structure_id)

    else:

        update_reserved_seats(doc)             
        delete_permissions(doc)
        delete_course_enrollment(doc)
        update_student(doc) 

def on_submit(doc,method):
    fee_structure_id = get_fee_structure(doc)
    
    if len(fee_structure_id)!=0:
           
        current_year_data = frappe.get_all("Program Enrollment",{'student':doc.student,'docstatus':1},['student','name','program','programs','student_batch_name',
                                    'student_name','roll_no','student_category','academic_year','academic_term'],limit=1)
                                 
        year_data = frappe.get_all("Program Enrollment",{'student':current_year_data[0]['student'],'docstatus':1,'program':current_year_data[0]['program'],
                        'programs':current_year_data[0]['programs']},['student','name','program','programs','student_batch_name','student_name','roll_no','student_category',
                        'academic_year','academic_term'])
       
        
        year_back="No"
        for t in year_data:
            if current_year_data[0]['program']== t['program'] and current_year_data[0]['programs'] == t['programs'] and current_year_data[0]['academic_year']==t['academic_year']:
                pass 
            else:
               year_back="Yes"     
       
        if year_back=="No":
            create_fees(doc,fee_structure_id,on_submit=1)
        else:
            frappe.msgprint("Student is a Year back so fees is not charged.")  

def get_fee_structure(doc):
    existed_fs = frappe.db.get_list("Fee Structure", {'programs':doc.programs, 'program':doc.program, 
                 'fee_type':'Semester Fees', 'academic_year':doc.academic_year,
                  'academic_term':doc.academic_term, 'docstatus':1},["name"])
    
    if len(existed_fs) != 0:                            
        fee_structure_id = existed_fs[0]['name']        
        term_date = frappe.get_all("Academic Term",{'name': doc.academic_term},['term_start_date','term_end_date'])
        if term_date == None:
            frappe.throw("Academic Term Start Date,End Date Not Found.")
        return fee_structure_id 
    elif len(existed_fs) == 0:
        frappe.msgprint("Fees not found.")
        return existed_fs


def fee_structure_validation(doc): 
   
    existed_fs = frappe.db.get_list("Fee Structure", {'programs':doc.programs, 'program':doc.program, 
                 'fee_type':'Semester Fees', 'academic_year':doc.academic_year,
                  'academic_term':doc.academic_term, 'docstatus':1},["name"])
    
    if len(existed_fs) != 0:                            
        fee_structure_id = existed_fs[0]['name']        
        term_date = frappe.get_all("Academic Term",{'name': doc.academic_term},['term_start_date','term_end_date'])
        if term_date == None:
            frappe.throw("Academic Term Start Date,End Date Not Found")
        return fee_structure_id 
    elif len(existed_fs) == 0:
        frappe.msgprint("Fees not charged. Proceed for program enrollment")
        return existed_fs

def create_fees(doc,fee_structure_id,on_submit=0):
    
    data = frappe.get_all("Program Enrollment",{'student':doc.student,'docstatus':1},['name','program','programs','student_batch_name',
                          'student_name','roll_no','student_category','academic_year','academic_term'],limit=1)
    
    term_date = frappe.get_all("Academic Term",{'name': doc.academic_term},['term_start_date','term_end_date'])
    fees = frappe.new_doc("Fees")
    fees.student = doc.student
    fees.student_name = doc.student_name    
    fees.valid_from = term_date[0]['term_start_date']
    fees.valid_to = term_date[0]['term_end_date']
    fees.due_date = doc.due_date
    fees.program_enrollment = data[0]['name']
    fees.program = data[0]['program']
    fees.programs = data[0]['programs']
    fees.student_batch = data[0]['student_batch_name']
    fees.academic_year= data[0]['academic_year']
    fees.academic_term=data[0]['academic_term']                 
    fees.fee_structure = fee_structure_id
    ref_details = frappe.get_all("Fee Component",{"parent":fee_structure_id},['fees_category','amount','receivable_account','income_account','company','grand_fee_amount','outstanding_fees'])
    for i in ref_details:
        fees.append("components",{
            'fees_category' : i['fees_category'],
            'amount' : i['amount'],
            'receivable_account' : i['receivable_account'],
            'income_account' : i['income_account'],
            'company' : i['company'],
            'grand_fee_amount' : i['grand_fee_amount'],
            'outstanding_fees' : i['outstanding_fees'],
        })
    if doc.due_date == None:                           
             frappe.throw("Enter the Due Date.")
    fees.save()
    fees.submit()
    frappe.db.set_value("Program Enrollment",doc.name, "voucher_no",fees.name) 
    doc.voucher_no=fees.name
    
    

def cancel_fees(doc,fee_structure_id):
    # cancel_doc = frappe.get_doc("Fees",voucher_no)
    # cancel_doc.cancel()
    for ce in frappe.get_all("Fees",{"program_enrollment":doc.name,"fee_structure":fee_structure_id}):
        make_reverse_gl_entries(voucher_type="Fees", voucher_no=ce.name)
    
      
def update_reserved_seats(doc,on_submit=0):
    if doc.reference_doctype and doc.reference_name and doc.reference_doctype in ["Student Applicant","Branch Sliding Application"]:

        # for applicant
        if doc.reference_doctype == "Student Applicant":
            
            for ad in frappe.get_all("Program Priority",{"parent":doc.reference_name,"programs":doc.programs,"semester":doc.program},["student_admission"]):
                admission=frappe.get_doc("Student Admission",ad.student_admission)

                # check reservation type exists
                if len(frappe.get_all("Reservations List",{"seat_reservation_type":doc.seat_reservation_type,"parent":admission.name}))==0:
                    frappe.throw("Reservation Type <b>{0}</b> Not Exists in Admission <b>{1}</b>".format(doc.seat_reservation_type,admission.name))

                # check checkbox values
                for reservation_type in frappe.get_all("Seat Reservation Type",{"name":doc.seat_reservation_type},["physically_disabled","award_winner","name"]):
                    
                    if doc.physically_disabled != reservation_type.physically_disabled:
                        frappe.throw("Please Mark Checkbox <b>{0}</b> for Reservation Type <b>{1}</b>".format("Physically Disabled",doc.seat_reservation_type)) 

                    if doc.award_winner != reservation_type.award_winner:
                        frappe.throw("Please Mark Checkbox <b>{0}</b> for Reservation Type <b>{1}</b>".format("Award Winner",doc.seat_reservation_type))

                    validate_reservation_type_by_criteria(doc,reservation_type.name)

                # update seat 
                for d in admission.get("reservations_distribution"):
                    if doc.seat_reservation_type==d.seat_reservation_type:
                        if on_submit:
                            d.seat_balance-=1
                        else:
                            d.seat_balance+=1
                admission.save()
        
        # branch sliding
        else:
            for application in frappe.get_all("Branch Sliding Application",{"name":doc.reference_name},['branch_sliding_declaration','sliding_in_program']):
                if application.branch_sliding_declaration:
                    declaration=frappe.get_doc("Branch sliding Declaration",application.branch_sliding_declaration)

                    for criteria in declaration.get("branch_sliding__criteria"):
                        if criteria.program==application.sliding_in_program:
                            if on_submit:
                                criteria.available_seats-=1
                            else:
                                criteria.available_seats+=1
                                
                    declaration.validate_seats()
                    declaration.submit()
def delete_permissions(doc):          
    delete_ref_doctype_permissions(["Programs","Course Enrollment","Course"],doc)
def delete_course_enrollment(doc):
    for ce in frappe.get_all("Course Enrollment",{"program_enrollment":doc.name}):
        frappe.delete_doc("Course Enrollment",ce.name)  
def update_student(doc):
    student=frappe.get_doc("Student",doc.student)
    student.set("current_education",[])
    for enroll in frappe.get_all("Program Enrollment",{"docstatus":1,"student":doc.student},limit=1):
        student.append("current_education",{
            "programs":doc.programs,
            "semesters":doc.program,
            "academic_year":doc.academic_year,
            "academic_term":doc.academic_term
        })
    student.save()  



             
             
            
                                  




