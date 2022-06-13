# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on
from frappe import ValidationError, _, scrub, throw
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from numpy import append
from six import iteritems, string_types

class PaymentRefund(Document):
    def validate(self):
        recon_rtgs_neft(self)
        if self.payment_type == "Pay":
            tot = 0
            refund_fee_info=frappe.get_all("GL Entry",filters=[["account","like","%Fees Refundable / Adjustable%"],["party","like",self.party]],fields=['name','debit','credit'])
            for t in refund_fee_info:
                tot += t['credit']-t['debit']
            for t in self.get("references"):
                if t.allocated_amount > tot:
                    frappe.throw("Allocated Amount must be less than Refundable Amount")
        elif self.payment_type == "Receive":
            tot = 0
            refund_fee_info=frappe.get_all("Fees",filters=[["outstanding_amount",">",0],["student","=",self.party]],fields=['name','outstanding_amount'])
            if (len(refund_fee_info) != 0):
                frappe.throw("Outstanding Amount is present for this party. Please clear the Outstanding Amount first!")
            else:
                pass



    def on_submit(self):
        if self.payment_type == "Pay":
            je_pay(self)
        elif self.payment_type == "Receive":
            je_receive(self)
        recon_rtgs_neft_on_submit(self)

    def on_cancel(self):
        cancel_doc = frappe.get_doc("Journal Entry",self.jv_entry_voucher_no)
        cancel_doc.cancel()

        

@frappe.whitelist()
def paid_from_fetch(mode_of_payment,company):
	mode_of_payment=frappe.get_all("Mode of Payment Account",{"parent":mode_of_payment,'company': company},['name','company','default_account'])
	if len(mode_of_payment)==0:
		frappe.throw("Account not maintained in Mode of Payment")
	else:
		return mode_of_payment[0]['default_account']	



def recon_rtgs_neft(self):
    if self.mode_of_payment=="NEFT" or self.mode_of_payment=="RTGS" or self.mode_of_payment=="IMPS":
        if self.reference_no==None:
            frappe.throw("Reference UTR No. not maintaned")
        else:
            Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":self.reference_no,"type_of_transaction":self.mode_of_payment,"docstatus":1},
                                        ["name","amount","total_allocated_amount","date","party_name"])
            if len(Recon_info)!=0:
                Recon_info=Recon_info[0]
                if Recon_info["party_name"]==None:
                    allocated_amount=0
                    for t in self.get("references"):
                        allocated_amount=allocated_amount+t.allocated_amount
                    if Recon_info['total_allocated_amount']==allocated_amount:
                        if Recon_info['total_allocated_amount']>=allocated_amount:
                            self.reference_date=Recon_info['date']
                        else:
                            frappe.throw("Paid Amount is more than Reconciled Amount")
                    else:
                        frappe.throw("Total Allocated Amount of BRS is not matching with present Allocated amount")        
                elif Recon_info["party_name"]==self.party:
                    if Recon_info['total_allocated_amount']>0:
                        if Recon_info['total_allocated_amount']>=allocated_amount:
                            self.reference_date=Recon_info['date'] 
                        else:
                            frappe.throw("Paid Amount is more than Reconciled Amount")                
                    else:
                        frappe.throw("Allocated Amount of BRS should be more then 0") 
                else:
                    frappe.throw("This UTR Belongs to other Student")            
            else:
                frappe.throw("UTR not Found")
        

def recon_rtgs_neft_on_submit(self):
    if self.mode_of_payment=="NEFT" or self.mode_of_payment=="RTGS" or self.mode_of_payment=="IMPS":
        Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":self.reference_no,"type_of_transaction":self.mode_of_payment},
                                ["name","amount","total_allocated_amount","date","count"])                     
        Recon_info=Recon_info[0]
        allocated_amount=0
        for t in self.get("references"):
            allocated_amount=allocated_amount+t.allocated_amount
        Grant_total_amount=Recon_info['total_allocated_amount']-allocated_amount
        count=int(Recon_info["count"])+1
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"total_allocated_amount",Grant_total_amount)
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"party_name",self.party)
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"count",count)
        st_upload_data=frappe.get_all("Payment Details Upload",{"brs_name":Recon_info['name'],"docstatus":1},['name'])
        if len(st_upload_data)!=0:
            frappe.db.set_value("Payment Details Upload",st_upload_data[0]['name'],"payment_status",1)
            frappe.db.set_value("Payment Details Upload",st_upload_data[0]['name'],"payment_id",self.name)  


# def je_pay(self):
#     je = frappe.new_doc("Journal Entry")
#     je.posting_date = self.posting_date
#     ref_details = frappe.get_all("Payment Refund",{"name":self.name},['party_type','party','paid_from','cost_center','paid_from_account_currency'])
#     ref_details_cd = frappe.get_all("Payment Entry Reference Refund",filters={"parent":self.name},fields=['account_paid_from','total_amount'])
#     ################################Cash Entry###################################
#     je.append("accounts",{
#     'account' : ref_details[0]['paid_from'],
#     'party_type' : ref_details[0]['party_type'],
#     'party' : ref_details[0]['party'],
#     'credit_in_account_currency' : ref_details_cd[0]['total_amount'],
#     'cost_center' : ref_details[0]['cost_center'],
#     'account_currency': ref_details[0]['paid_from_account_currency'],
#     'balance': get_balance_on(ref_details[0]['paid_from'], self.posting_date, cost_center=ref_details[0]['cost_center'])
#     })
#     #################################Refundable Entry##############################
#     je.append("accounts",{
#     'account' : ref_details_cd[0]['account_paid_from'],
#     'party_type' : ref_details[0]['party_type'],
#     'party' : ref_details[0]['party'],
#     'debit_in_account_currency' : ref_details_cd[0]['total_amount'],
#     'cost_center' : ref_details[0]['cost_center'],
#     'account_currency': ref_details[0]['paid_from_account_currency'],
#     'balance': get_balance_on(ref_details_cd[0]['account_paid_from'], self.posting_date, cost_center=ref_details[0]['cost_center'])
#     })
#     je.save()
#     je.submit()
#     self.jv_entry_voucher_no=je.name
#     frappe.db.set_value("Payment Refund",self.name,"jv_entry_voucher_no",je.name)


def je_pay(self):
    for d in self.get("references"):
        t=d.total_amount
        acc=d.account_paid_from
    je = frappe.new_doc("Journal Entry")
    je.posting_date = self.posting_date
    je.append("accounts",{
    'account' : self.paid_to,
    'party_type' : self.party_type,
    'party' : self.party,
    'credit_in_account_currency' : t,
    'cost_center' : self.cost_center,
    'account_currency': self.paid_to_account_currency,
    'balance': get_balance_on(self.paid_to, self.posting_date, cost_center=self.cost_center)
    })
    
    je.append("accounts",{
    'account' : acc,
    'party_type' : self.party_type,
    'party' : self.party,
    'debit_in_account_currency' : t,
    'cost_center' : self.cost_center,
    'account_currency': self.paid_to_account_currency,
    'balance': get_balance_on(acc, self.posting_date, cost_center=self.cost_center)
    })
    je.save()
    je.submit()
    self.jv_entry_voucher_no=je.name
    frappe.db.set_value("Payment Refund",self.name,"jv_entry_voucher_no",je.name)



# def je_receive(self):
#     je = frappe.new_doc("Journal Entry")
#     je.posting_date = self.posting_date
#     ref_details = frappe.get_all("Payment Refund",{"name":self.name},['party_type','party','paid_to','cost_center','paid_to_account_currency'])
#     ref_details_cd = frappe.get_all("Payment Entry Reference Refund",filters={"parent":self.name},fields=['account_paid_to','total_amount'])
#     ################################Cash Entry###################################
#     je.append("accounts",{
#     'account' : ref_details_cd[0]['account_paid_to'],
#     'party_type' : ref_details[0]['party_type'],
#     'party' : ref_details[0]['party'],
#     'credit_in_account_currency' : ref_details_cd[0]['total_amount'],
#     'cost_center' : ref_details[0]['cost_center'],
#     'account_currency': ref_details[0]['paid_to_account_currency'],
#     'balance': get_balance_on(ref_details_cd[0]['account_paid_to'], self.posting_date, cost_center=ref_details[0]['cost_center'])
#     })
#     #################################Refundable Entry##############################
#     je.append("accounts",{
#     'account' : ref_details[0]['paid_to'],
#     'party_type' : ref_details[0]['party_type'],
#     'party' : ref_details[0]['party'],
#     'debit_in_account_currency' : ref_details_cd[0]['total_amount'],
#     'cost_center' : ref_details[0]['cost_center'],
#     'account_currency': ref_details[0]['paid_to_account_currency'],
#     'balance': get_balance_on(ref_details[0]['paid_to'], self.posting_date, cost_center=ref_details[0]['cost_center'])
#     })
#     je.save()
#     je.submit()
#     self.jv_entry_voucher_no=je.name
#     frappe.db.set_value("Payment Refund",self.name,"jv_entry_voucher_no",je.name)


def je_receive(self):
    for d in self.get("references"):
        t=d.total_amount
        acc=d.account_paid_to
    je = frappe.new_doc("Journal Entry")
    je.posting_date = self.posting_date
    je.append("accounts",{
    'account' : self.paid_from,
    'party_type' : self.party_type,
    'party' : self.party,
    'debit_in_account_currency' : t,
    'cost_center' : self.cost_center,
    'account_currency': self.paid_from_account_currency,
    'balance': get_balance_on(self.paid_from, self.posting_date, cost_center=self.cost_center)
    })
    
    je.append("accounts",{
    'account' : acc,
    'party_type' : self.party_type,
    'party' : self.party,
    'credit_in_account_currency' : t,
    'cost_center' : self.cost_center,
    'account_currency': self.paid_from_account_currency,
    'balance': get_balance_on(acc, self.posting_date, cost_center=self.cost_center)
    })
    je.save()
    je.submit()
    self.jv_entry_voucher_no=je.name
    frappe.db.set_value("Payment Refund",self.name,"jv_entry_voucher_no",je.name)

