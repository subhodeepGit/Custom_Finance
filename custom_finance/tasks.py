import frappe

# Auto Email through hooks Scheduler
def cron():

    msg="""<b>Dear Student,</b><br>"""
    msg+="""<p>Your Payment Details Upload are not reconciled yet. You can check your UTR number If your UTR number and all details are correct then ignore this mail. </p><br>"""
    unreconciliated_data= frappe.get_all("Payment Details Upload",{"reconciliation_status":0,"payment_status":0,"docstatus":1}, ["student"])
    recipients=[]
    for t in unreconciliated_data:
        data= frappe.db.get_value("Student",{"name":t['student']},"student_email_id")
        recipients.append(data)
        if len(recipients)!=0:
                    send_mail(recipients,'Payment Reconciled',msg)

def send_mail(recipients,subject,message):
    if has_default_email_acc():
        frappe.sendmail(recipients=recipients,subject=subject,message=message,with_container=True)

def has_default_email_acc():
    for d in frappe.get_all("Email Account", {"default_outgoing":1}):
       return "true"
    return ""