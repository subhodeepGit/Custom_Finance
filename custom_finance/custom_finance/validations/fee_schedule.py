import frappe
from kp_edtec.kp_edtec.utils import duplicate_row_validation

def validate(doc, method):
    validate_academic_year(doc)
    validate_semester(doc)
    duplicate_row_validation(doc, "student_groups", ['student_group',])

def validate_academic_year(doc):
    if doc.academic_term:
        if doc.academic_term not in [d.name for d in frappe.get_all("Academic Term", {'academic_year':doc.get('academic_year')},['name'])]:
            frappe.throw("Academic Term <b>'{0}'</b> not belongs to academic year <b>'{1}'</b>".format(doc.get('academic_term'), doc.get('academic_year')))

def validate_semester(doc):
    if doc.program not in [d.semesters for d in frappe.get_all("Semesters", {'parent':doc.get('programs')},['semesters'])]:
        frappe.throw("Semester <b>'{0}'</b> not belongs to program <b>'{1}'</b>".format(doc.get('program'), doc.get('programs')))
