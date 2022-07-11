import frappe
from re import L
from frappe.utils.data import format_date
from frappe.utils import get_url_to_form
from frappe.utils import cint, cstr, parse_addr
from stripe import Recipient

def payment_entry_submit(doc):
    msg="""<p><b>Payment is Sucessfull</b></p><br>"""
    msg+="""<b>---------------------Payment Details---------------------</b><br>"""
    msg+="""<p>---------------------Type of Payment---------------------</p><br>"""
    msg+="""<b>Payment Entry No.:</b>  {0}<br>""".format(doc.get('name'))
    msg+="""<b>Date:</b>  {0}<br>""".format(format_date(doc.get('posting_date'), 'dd/mm/yyyy'))
    msg+="""<p>---------------------Payment From / TO---------------------</p><br>"""
    msg+="""<b>Name:</b>  {0}<br>""".format(doc.get('party_name') or '-')
    msg+="""<b>Roll Number:</b>  {0}<br>""".format(doc.get('roll_no') or '-' )
    msg+="""<b>Amount Paid:</b>  {0}<br>""".format(doc.get('paid_amount') or '-' )
    recipients = frappe.db.get_value("Student",doc.get('party'),"student_email_id")
    attachments = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name, print_format='Payment Entry Money Recipt')]
    send_mail(recipients,'Payment Successful',msg,attachments)


def unreconciled_utr(doc):
    msg="""<p><b>Payment Reconciled</b></p><br>"""
    msg+="""<b>Dear Student,</b><br>"""
    msg+="""<p>Your Payment details Upload are not reconciled yet. You can check your UTR No. if Your UTR No. and all details are correct then ignore this mail. </p><br>"""
    unreconciliated_data= frappe.get_all("Payment Details Upload",{"name":doc.get('name'),"reconciliation_status":0,"payment_status":0}, ["student"])
    # [{"student_email_id":"adas@kiit.ac"}]
    recipients=[]
    for t in unreconciliated_data:
        data= frappe.db.get_value("Student",{"name":t['student']},"student_email_id")
        recipients.append(data)
    attachments = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name, print_format='')]
    send_mail(recipients,'Payment Reconciled',msg,attachments)

def send_mail(recipients,subject,message,attachments):
    if has_default_email_acc():
        frappe.sendmail(recipients=recipients,subject=subject,message=message,attachments=attachments,with_container=True)

def has_default_email_acc():
    for d in frappe.get_all("Email Account", {"default_outgoing":1}):
       return "true"
    return ""
