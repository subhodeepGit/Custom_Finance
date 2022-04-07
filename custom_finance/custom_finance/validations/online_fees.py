import frappe
from frappe.model.document import Document
from datetime import date


def on_submit(self,methord):
    # branch_change_application_paid(self)
    if self.mode_of_payment=="Online Payment":
        from razorpay_integration.api import get_razorpay_checkout_url
        doctype='Payment Entry'
        try:
            out=frappe.db.sql(""" select `razorpay_id` from `tabPayment Entry` where `name`="%s" """%(self.name))
            razorpay_id=out[0][0]
            if razorpay_id==None:
                frappe.throw("Payment is not successful.Please contact to Account section or Retry for payment")
            else:
                frappe.msgprint("Payment Sucessfull. Transaction Id <b>%s </b> "%(self.razorpay_id))
                pass
        except:
            frappe.throw("Please contact Accounts Section")
@frappe.whitelist(allow_guest=True)
def make_payment(full_name, email_id,amount,doctype,name):
    from razorpay_integration.api import get_razorpay_checkout_url
    url = get_razorpay_checkout_url(**{
        'amount': amount,
        'title': 'Online payment',
        'description': 'Online payment',
        'payer_name': full_name,
        'payer_email': email_id,
        'doctype':doctype,
        'name': name,
        'order_id':name
    })
    # webbrowser.open(url)
    return url

@frappe.whitelist(allow_guest=True)
def paid_from_account_type(reference_no=None,mode_of_payment=None):
    date=""
    Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":reference_no,"type_of_transaction":mode_of_payment},
                                        ["name","amount","total_allocated_amount","date","party_name"])
    if len(Recon_info)!=0:
        date=Recon_info[0]["date"]
    return date    