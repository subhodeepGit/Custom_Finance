import frappe
from frappe.model.mapper import get_mapped_doc
from kp_edtec.kp_edtec.utils import duplicate_row_validation

def on_submit(doc,method):
    if doc.exam_application:
        ex=frappe.get_doc("Exam Application",doc.exam_application)
        ex.status="Paid"
        ex.flags._validate_update_after_submit = True
        ex.submit()
        
    if doc.program_enrollment and not doc.programs:
        doc.programs=frappe.db.get_value("Program Enrollment",doc.program_enrollment,'programs')
    
    if doc.is_return and doc.return_against:
        return_against=frappe.get_doc("Fees",doc.return_against)
        return_against.return_issued=1
        return_against.submit()

def on_cancel(doc,method):
     if doc.is_return and doc.return_against:
        return_against=frappe.get_doc("Fees",doc.return_against)
        return_against.return_issued=0
        return_against.submit()

def validate(doc,method):
    validate_amount(doc)
    duplicate_row_validation(doc, "components", ['fees_category', 'amount'])
    # doc.calculate_amount()

# def calculate_amount(self):
# 		for events in self.get("components"):
# 			events.grand_fee_amount=events.amount
# 			events.outstanding_fees=events.amount

def validate_amount(doc):
    if doc.is_return:
        for cmp in doc.components:
            if cmp.amount>0:
                frappe.throw("Component <b>{0}</b> amount Must be <b>-ve</b> value".format(cmp.fees_category))
        if doc.grand_total>0:
            frappe.throw("Grand Total Must be <b>-ve</b> value")

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_fee_structures(doctype, txt, searchfield, start, page_len, filters):
    program=""
    for d in frappe.get_all("Current Educational Details",{"parent":filters.get("student")},['semesters']):
        program+=d.semesters
    return frappe.db.sql("""select name,program,student_category,academic_year from `tabFee Structure` where program IN ('{0}') and (name like '%{1}%' or program like '%{1}%' or student_category like '%{1}%' or academic_year like '%{1}%')""".format(program,txt))

@frappe.whitelist()
def get_progarms(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"programs":txt})

    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['programs'],as_list=1)
    return data

@frappe.whitelist()
def get_sem(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"program":txt})

    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['program'],as_list=1)
    return data 


@frappe.whitelist()
def get_term(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"academic_term":txt})

    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['academic_term'],as_list=1)
    return data

@frappe.whitelist()
def get_year(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"academic_year":txt})

    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['academic_year'],as_list=1)
    return data 

@frappe.whitelist()
def get_batch(doctype, txt, searchfield, start, page_len, filters):
    fltr = {'docstatus':1}
    if txt:
        fltr.update({"student_batch_name":txt})

    fltr.update({"student":filters.get("student")})
    data = frappe.get_all("Program Enrollment",fltr,['student_batch_name'],as_list=1)
    return data 


@frappe.whitelist()
def get_student_category(doctype, txt, searchfield, start, page_len, filters):
    fltr = {}
    lst = []
    if txt:
        fltr.update({"student_category":txt})
    fltr.update({"student":filters.get("student")})
    for i in frappe.get_all("Program Enrollment",fltr,['student_category']):
        if i.student_category not in lst:
            lst.append(i.student_category)
    return [(d,) for d in lst]

@frappe.whitelist()
def get_fees_category(doctype, txt, searchfield, start, page_len, filters):
    fltr = {}
    lst = []
    if txt:
        fltr.update({"fees_category":txt})
    
    fltr.update({"parent":filters.get("fee_structure"),"parenttype":"Fee Structure"})
    for i in frappe.get_all("Fee Component",fltr,['fees_category'],order_by="idx asc"):
        if i.fees_category not in lst:
            lst.append(i.fees_category)
    return [(d,) for d in lst]

@frappe.whitelist()
def make_refund_fees(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.set("components",[])
        for d in source.get("components"):
            target.append("components",{
					"fees_category":d.fees_category,
					"amount":-d.amount,
					"description":d.description,
                    "income_account":d.income_account,
                    "receivable_account":d.receivable_account
				})
        target.grand_total=(-source.grand_total)
        target.is_return=1
        target.return_against=source.name
        target.outstanding_amount=(-source.outstanding_amount)

    doclist = get_mapped_doc("Fees", source_name, 	{
        "Fees": {
            "doctype": "Fees",
        },
    }, target_doc, set_missing_values)

    return doclist
@frappe.whitelist()
def get_fee_components(fee_structure):
    """Returns Fee Components.

    :param fee_structure: Fee Structure.
    """
    if fee_structure:
        fs = frappe.get_all("Fee Component", fields=["fees_category", "description", "amount","receivable_account",
                                                    "income_account","grand_fee_amount","outstanding_fees","waiver_type","percentage","waiver_amount",
                                                    "total_waiver_amount"] , 
                                                filters={"parent": fee_structure}, order_by= "idx asc")
        return fs


