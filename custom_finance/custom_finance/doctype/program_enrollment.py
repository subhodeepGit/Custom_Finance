import frappe
from erpnext.accounts.general_ledger import make_reverse_gl_entries

def on_cancel(doc,method):
    cancel_fees(doc)#Rupali:Semester fees added:10May2022 

def on_submit(doc,method):
    fee_structure_id = fee_structure_validation(doc)
    create_fees(doc,fee_structure_id,on_submit=1) #Rupali:Semester fees added:30Apr2022 

# Rupali:Semester fees added during program enrollment:30Apr2022  :start #KP
def fee_structure_validation(doc): 
   
    existed_fs = frappe.db.get_list("Fee Structure", {'programs':doc.programs, 'program':doc.program, 
                 'student_category':doc.student_category,'fee_type':'Semester Fees', 'academic_year':doc.academic_year,
                  'academic_term':doc.academic_term, 'docstatus':1},["name"])
   
    if len(existed_fs) != 0:
        fee_structure_id = existed_fs[0]['name']
        return fee_structure_id
    else:
        frappe.throw("Fee Structure Not Found")
    term_date = frappe.get_all("Academic Term",{'name': doc.term_name},['term_start_date','term_end_date'])

    if term_date == None:
        frappe.throw("Academic Term Start Date,End Date Not Found")

def create_fees(doc,fee_structure_id,on_submit=0):
    data = frappe.get_all("Program Enrollment",{'student':doc.student,'docstatus':1},['name','program','programs','student_batch_name',
                          'student_name','roll_no','student_category','academic_year','academic_term'],limit=1)
    
    term_date = frappe.get_all("Academic Term",{'name': doc.academic_term},['term_start_date','term_end_date'])
    fees = frappe.new_doc("Fees")
    fees.student = doc.student
    fees.student_name = doc.student_name    
    fees.valid_from = term_date[0]['term_start_date']
    fees.valid_to = term_date[0]['term_end_date']
    fees.due_date = term_date[0]['term_end_date']
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
      
    fees.save()
    fees.submit()

def cancel_fees(doc):
    for ce in frappe.get_all("Fees",{"program_enrollment":doc.name}):
        make_reverse_gl_entries(voucher_type="Fees", voucher_no=ce.name)
      

# Rupali:Semester fees added:30Apr2022  :end   #KP
