import frappe
from erpnext.accounts.general_ledger import make_reverse_gl_entries



def validate(doc,method):                           #Rupali:program enrollment done whether FS is there or not:27thMay2022
    fee_structure_id = fee_structure_validation(doc)

def on_cancel(doc,method):
    fee_structure_id = fee_structure_validation(doc)
    cancel_fees(doc,fee_structure_id) #Rupali:Semester fees added:10May2022 

def on_submit(doc,method):
    fee_structure_id = fee_structure_validation(doc)
    if len(fee_structure_id)!=0:
       
        current_year_data = frappe.get_all("Program Enrollment",{'student':doc.student,'docstatus':1},['name','program','programs','student_batch_name','student_name','roll_no','student_category','academic_year','academic_term'],limit=1)
        year_data = frappe.get_all("Program Enrollment",{'student':doc.student,'docstatus':1,'program':doc.program,'programs':doc.programs},['name','program','programs','student_batch_name','student_name','roll_no','student_category','academic_year','academic_term'])
        if current_year_data[0]['program']== year_data[0]['program'] and current_year_data[0]['programs'] == year_data[0]['programs'] :
             frappe.msgprint("Fees not charged. Proceed for program enrollment")

            
             create_fees(doc,fee_structure_id,on_submit=1) #Rupali:Semester fees added:30Apr2022 
        else:
            create_fees(doc,fee_structure_id,on_submit=1) #Rupali:Semester fees added:30Apr2022 



       
        
       
        # create_fees(doc,fee_structure_id,on_submit=1) #Rupali:Semester fees added:30Apr2022 
        
# Rupali:Semester fees added during program enrollment:30Apr2022  :start #KP
def fee_structure_validation(doc): 
   
    existed_fs = frappe.db.get_list("Fee Structure", {'programs':doc.programs, 'program':doc.program, 
                 'fee_type':'Semester Fees', 'academic_year':doc.academic_year,
                  'academic_term':doc.academic_term, 'docstatus':1},["name"])
   
    if len(existed_fs) != 0:                             #Rupali:Modified the code for PE and FS :27thMay2022
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
    if doc.due_date == None:                            #Rupali:30thMay2022: added to check date mandatory through code wise.
             frappe.throw("Enter the Due Date.")
    fees.save()
    fees.submit()
    frappe.db.set_value("Program Enrollment",doc.name, "voucher_no",fees.name) 

def cancel_fees(doc,fee_structure_id):
    for ce in frappe.get_all("Fees",{"program_enrollment":doc.name,"fee_structure":fee_structure_id}):
        make_reverse_gl_entries(voucher_type="Fees", voucher_no=ce.name)
      

# Rupali:Semester fees added:30Apr2022  :end   #KP

