from typing_extensions import Self
from unicodedata import name
import frappe
import datetime

def validate(self,method):
    bank_draft_amount(self)
    recon_rtgs_neft(self)
    allocation_amount(self)
    online_payment(self)
    if self.mode_of_payment=="Fees Refundable / Adjustable":   
        refundable_amount(self)
    calucate_total(self) 

def on_update(self,method):
    pass

def on_submit(self,method):
    recon_rtgs_neft_on_submit(self)
    online_payment_on_submit(self)    
    child_table_fees_outsatnding(self)
    refundable_fees_outsatnding(self,cancel=0)   

def on_cancel(self,method):
    child_table_fees_outsatnding(self)
    refundable_fees_outsatnding(self,cancel=1)
    recon_rtgs_neft_on_cancel(self)
    online_payment_on_cancel(self)


def online_payment(self):
    if self.mode_of_payment=="Online Payment":
        if self.reference_no==None:
            frappe.throw("Reference Transaction ID. not maintaned")
        else:
            Recon_info=frappe.get_all("ICICI Online Payment",{"transaction_id":self.reference_no,"transaction_status":"SUCCESS","docstatus":1,"payment_status":0},
                                                        ["name","date_time_of_transaction","paying_amount","total_outstanding_amout","party"])
            if Recon_info:
                Recon_info=Recon_info[0]
                if self.party==Recon_info["party"]:
                    if Recon_info['paying_amount']>=self.total_allocated_amount:
                        date_time_str = Recon_info["date_time_of_transaction"]
                        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
                        date=date_time_obj.date()
                        self.reference_date=date
                        flag="pass"
                        for t in self.get('references'):
                            if t.fees_category=="Fees Refundable / Adjustable":
                                flag="no_pass"
                                break 
                        if Recon_info['paying_amount']>self.total_allocated_amount and flag=="pass":
                                Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']],fields=['name'])
                                if not Account:
                                    frappe.throw("Fees Refundable / Adjustable not mantained for the comapny")
                                reference_name=""
                                allocated_excess_amount=0
                                for t in self.get('references'):
                                    allocated_excess_amount=allocated_excess_amount+t.allocated_amount 
                                paid_amount=allocated_excess_amount      
                                allocated_excess_amount=Recon_info['paying_amount']-allocated_excess_amount  
                                paid_amount=paid_amount+allocated_excess_amount
                                self.total_allocated_amount=paid_amount
                                self.difference_amount=paid_amount-self.total_allocated_amount
                                for t in self.get('references'):
                                    reference_name=t.reference_name
                                    due_date=t.due_date
                                    break
                                if self.payment_type=="Receive":
                                    self.append("references",{
                                        "reference_doctype":"Fees",
                                        "fees_category":"Fees Refundable / Adjustable",
                                        "account_paid_from":Account[0]['name'],
                                        "reference_name":reference_name,
                                        "allocated_amount":allocated_excess_amount,
                                        "total_amount":allocated_excess_amount,
                                        "outstanding_amount":allocated_excess_amount,
                                        "due_date":due_date,
                                        "exchange_rate":1,
                                    })
                        elif Recon_info['paying_amount']>self.total_allocated_amount and flag=="no_pass":
                                Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']],fields=['name'])
                                if not Account:
                                    frappe.throw("Fees Refundable / Adjustable not mantained for the comapny")
                                reference_name=""
                                allocated_excess_amount=0
                                for t in self.get('references'):
                                    if t.fees_category!="Fees Refundable / Adjustable":
                                        allocated_excess_amount=allocated_excess_amount+t.allocated_amount  
                                paid_amount=allocated_excess_amount      
                                allocated_excess_amount=Recon_info['paying_amount']-allocated_excess_amount  
                                paid_amount=paid_amount+allocated_excess_amount
                                self.total_allocated_amount=paid_amount
                                self.difference_amount=paid_amount-self.total_allocated_amount 

                                # allocated_excess_amount=Recon_info['total_allocated_amount']-allocated_excess_amount
                                for t in self.get('references'):
                                    reference_name=t.reference_name
                                    break 
                                count=0
                                for j in self.get('references'):
                                    count=count+j.allocated_amount  
                                for t in self.get('references'):
                                    # reference_name=t.reference_name
                                    if t.fees_category=="Fees Refundable / Adjustable":
                                        t.reference_doctype=t.reference_doctype
                                        t.fees_category="Fees Refundable / Adjustable"
                                        t.account_paid_from=Account[0]['name']
                                        t.reference_name=reference_name
                                        t.allocated_amount=allocated_excess_amount
                                        t.total_amount=allocated_excess_amount
                                        t.outstanding_amount=allocated_excess_amount
                        elif Recon_info['paying_amount']==self.total_allocated_amount:
                                pass
                    else:
                        frappe.throw("Paid Amount is more than Reconciled Amount") 
                else:
                    frappe.throw("Transaction ID. Belong to different studnet") 
            else:
                frappe.throw("Transaction ID. not Found")     

def online_payment_on_submit(self):
    if self.mode_of_payment=="Online Payment":
        Recon_info=frappe.get_all("ICICI Online Payment",{"transaction_id":self.reference_no,"transaction_status":"SUCCESS","docstatus":1,"payment_status":0},
                                                        ["name","date_time_of_transaction","paying_amount","total_outstanding_amout","party"])
        Recon_info=Recon_info[0]
        frappe.db.set_value("ICICI Online Payment",Recon_info['name'],"payment_status",1)
        frappe.db.set_value("ICICI Online Payment",Recon_info['name'],"payment_id",self.name)

def online_payment_on_cancel(self):
    if self.mode_of_payment=="Online Payment":
        Recon_info=frappe.get_all("ICICI Online Payment",{"transaction_id":self.reference_no},
                                                        ["name","date_time_of_transaction","paying_amount","total_outstanding_amout","party"])
        Recon_info=Recon_info[0]
        frappe.db.set_value("ICICI Online Payment",Recon_info['name'],"payment_status",0)
        frappe.db.set_value("ICICI Online Payment",Recon_info['name'],"payment_id","")

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
                    if Recon_info['total_allocated_amount']>0:
                        if Recon_info['total_allocated_amount']>=self.total_allocated_amount:
                            self.reference_date=Recon_info['date']
                            ##################### i have to complete here code 
                            # Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']])
                            flag="pass"
                            for t in self.get('references'):
                                if t.fees_category=="Fees Refundable / Adjustable":
                                    flag="no_pass"
                                    break 
                            if Recon_info['total_allocated_amount']>self.total_allocated_amount and flag=="pass":
                                Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']],fields=['name'])
                                if not Account:
                                    frappe.throw("Fees Refundable / Adjustable not mantained for the comapny")
                                reference_name=""
                                allocated_excess_amount=0
                                for t in self.get('references'):
                                    allocated_excess_amount=allocated_excess_amount+t.allocated_amount 
                                paid_amount=allocated_excess_amount      
                                allocated_excess_amount=Recon_info['total_allocated_amount']-allocated_excess_amount  
                                paid_amount=paid_amount+allocated_excess_amount
                                self.total_allocated_amount=paid_amount
                                self.difference_amount=paid_amount-self.total_allocated_amount
                                for t in self.get('references'):
                                    reference_name=t.reference_name
                                    due_date=t.due_date
                                    break
                                if self.payment_type=="Receive":
                                    self.append("references",{
                                        "reference_doctype":"Fees",
                                        "fees_category":"Fees Refundable / Adjustable",
                                        "account_paid_from":Account[0]['name'],
                                        "reference_name":reference_name,
                                        "allocated_amount":allocated_excess_amount,
                                        "total_amount":allocated_excess_amount,
                                        "outstanding_amount":allocated_excess_amount,
                                        "due_date":due_date,
                                        "exchange_rate":1,
                                    })
                            elif Recon_info['total_allocated_amount']>self.total_allocated_amount and flag=="no_pass":
                                Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']],fields=['name'])
                                if not Account:
                                    frappe.throw("Fees Refundable / Adjustable not mantained for the comapny")
                                reference_name=""
                                allocated_excess_amount=0
                                for t in self.get('references'):
                                    if t.fees_category!="Fees Refundable / Adjustable":
                                        allocated_excess_amount=allocated_excess_amount+t.allocated_amount  
                                paid_amount=allocated_excess_amount      
                                allocated_excess_amount=Recon_info['total_allocated_amount']-allocated_excess_amount  
                                paid_amount=paid_amount+allocated_excess_amount
                                self.total_allocated_amount=paid_amount
                                self.difference_amount=paid_amount-self.total_allocated_amount 

                                # allocated_excess_amount=Recon_info['total_allocated_amount']-allocated_excess_amount
                                for t in self.get('references'):
                                    reference_name=t.reference_name
                                    break 
                                count=0
                                for j in self.get('references'):
                                    count=count+j.allocated_amount  
                                for t in self.get('references'):
                                    # reference_name=t.reference_name
                                    if t.fees_category=="Fees Refundable / Adjustable":
                                        t.reference_doctype=t.reference_doctype
                                        t.fees_category="Fees Refundable / Adjustable"
                                        t.account_paid_from=Account[0]['name']
                                        t.reference_name=reference_name
                                        t.allocated_amount=allocated_excess_amount
                                        t.total_amount=allocated_excess_amount
                                        t.outstanding_amount=allocated_excess_amount
                            elif Recon_info['total_allocated_amount']==self.total_allocated_amount:
                                pass
                        else:
                            frappe.throw("Paid Amount is more than Reconciled Amount")
                    else:
                        frappe.throw("Allocated Amount of BRS should be more then 0")        
                elif Recon_info["party_name"]==self.party:
                    if Recon_info['total_allocated_amount']>0:
                        if Recon_info['total_allocated_amount']>=self.total_allocated_amount:
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
        Grant_total_amount=Recon_info['total_allocated_amount']-self.total_allocated_amount
        count=int(Recon_info["count"])+1
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"total_allocated_amount",Grant_total_amount)
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"party_name",self.party)
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"count",count)
        st_upload_data=frappe.get_all("Payment Details Upload",{"brs_name":Recon_info['name'],"docstatus":1},['name'])
        if len(st_upload_data)!=0:
            frappe.db.set_value("Payment Details Upload",st_upload_data[0]['name'],"payment_status",1)
            frappe.db.set_value("Payment Details Upload",st_upload_data[0]['name'],"payment_id",self.name)  


def recon_rtgs_neft_on_cancel(self):
    if self.mode_of_payment=="NEFT" or self.mode_of_payment=="RTGS" or self.mode_of_payment=="IMPS":
        Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":self.reference_no,"type_of_transaction":self.mode_of_payment},
                                ["name","amount","total_allocated_amount","date","count"])

        Recon_info=Recon_info[0]
        if int(Recon_info["count"])==1:
            frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"party_name",None)
        Grant_total_amount=Recon_info['total_allocated_amount']+self.total_allocated_amount  
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"total_allocated_amount",Grant_total_amount) 
        count=int(Recon_info["count"])-1
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"count",count)
        st_upload_data=frappe.get_all("Payment Details Upload",{"brs_name":Recon_info['name'],"docstatus":1},['name'])
        if len(st_upload_data)!=0:
            frappe.db.set_value("Payment Details Upload",st_upload_data[0]['name'],"payment_status",0)
            frappe.db.set_value("Payment Details Upload",st_upload_data[0]['name'],"payment_id",'')    

def child_table_fees_outsatnding(self):
    ### payment entry child doc
    z=self.get("references")
    reference_name=[]
    for i in z:
        reference_name.append(i.reference_name)
    reference_name = list(set(reference_name))   

 
    for v in reference_name:
        Outstanding_amount=[]
        payment_referance_fees_category=[]
        for d in self.get("references"):
            if d.allocated_amount:
                payment_referance_fees_category.append(d.fees_category)
                ref_details=frappe.get_all("Fee Component",{"parent":v,"fees_category":d.fees_category},["name","grand_fee_amount","outstanding_fees","fees_category"])
                for t in ref_details:
                    if t['fees_category']==d.fees_category:
                        Outstanding_amount.append(d.outstanding_amount)
                        frappe.db.set_value("Fee Component",t['name'], "outstanding_fees",d.outstanding_amount) 
        ref_details=frappe.get_all("Fee Component",filters=[["parent", "=",v], ["fees_category", "NOT IN", tuple(payment_referance_fees_category)]],fields=["name","grand_fee_amount","outstanding_fees","fees_category"])
        for t in ref_details:
            Outstanding_amount.append(t["outstanding_fees"])             
        frappe.db.set_value("Fees",v, "outstanding_amount",sum(Outstanding_amount))

def calucate_total(self):
    allocated_amount1=[]
    for d in self.get("references"):
        allocated_amount1.append(d.allocated_amount)   
    self.paid_amount=abs(sum(allocated_amount1))

def allocation_amount(self):
    role_profile_name = frappe.db.get_value("User",frappe.session.user, ["role_profile_name"], as_dict=True)
    if role_profile_name["role_profile_name"]=="Student":
        paid_amount=self.paid_amount
        for d in self.get("references"):
            # d.allocated_amount=300
            if d.outstanding_amount==paid_amount:
                d.allocated_amount=paid_amount
                paid_amount=paid_amount-d.allocated_amount
            elif d.outstanding_amount<paid_amount:
                d.allocated_amount=d.outstanding_amount
                paid_amount=paid_amount-d.outstanding_amount
            elif d.outstanding_amount>paid_amount:
                d.allocated_amount=paid_amount
                paid_amount=paid_amount-paid_amount  
            else:
                 d.allocated_amount=0   
    else:
        pass    


def refundable_fees_outsatnding(self,cancel):
    for d in self.get("references"):
        if d.fees_category=="Fees Refundable / Adjustable":
            if cancel==0:
                frappe.db.set_value("Payment Entry Reference",d.name, "outstanding_amount",0.0) 
                d.outstanding_amount=0.0
            elif cancel==1:  
                # frappe.db.set_value("Payment Entry Reference",d.name, "outstanding_amount",d.total_amount) 
                d.outstanding_amount=d.total_amount    


def refundable_amount(self):
    student=self.party
    gl_entry_fees=frappe.db.get_all("GL Entry",filters=[["party","=",student],["voucher_type","=",'Payment Entry'],['against_voucher_type','=','Fees'],
                            ['account','like','%Fees Refundable / Adjustable%'],["is_cancelled","=",0]],fields=["name","voucher_type","account","credit",'voucher_no'])
                        
    gl_entry_payment=frappe.db.get_all("GL Entry",filters=[["against","=",student],['voucher_type',"=","Payment Entry"],['account','like','%Fees Refundable / Adjustable %'],
                                    ["is_cancelled","=",0]],fields=["name","voucher_type","account","debit",'voucher_no'])
    gl_entry_payment_refund=frappe.db.get_all("GL Entry",filters=[["against","=",student],['voucher_type',"=","Journal Entry"],['account','like','%Fees Refundable / Adjustable %'],
                                            ["is_cancelled","=",0]],fields=["name","voucher_type","account","credit",'debit','voucher_no']) 
    ########################### Journal Entry
    recev_amount=0
    paid_amount=0
    for t in gl_entry_payment_refund:
        if t["debit"]!=0:
            paid_amount=paid_amount+t["debit"]
        if t["credit"]!=0:
            recev_amount=recev_amount+t["credit"]

    ############################### Fees type payment for Fees Refundable / Adjustable
    extra_amount_paid=0
    for t in gl_entry_fees:
        extra_amount_paid=extra_amount_paid+t['credit']
    extra_amount_paid=extra_amount_paid+recev_amount

    ################################## Adjustment voucher payment entry
    ref_amount_adjusted=0    
    for t in gl_entry_payment:
        ref_amount_adjusted=ref_amount_adjusted+t['debit']

    total_ref_amount_adjusted=ref_amount_adjusted+self.total_allocated_amount+paid_amount
    ##################################################################
    adjusted_amount=extra_amount_paid-total_ref_amount_adjusted
    if adjusted_amount>0:
        if extra_amount_paid >= self.total_allocated_amount:
            pass
        # elif extra_amount_paid <= self.paid_amount:
        #     total_paid_amount=0
        #     for d in self.get("references"):
        #         total_paid_amount=total_paid_amount+d.allocated_amount
        #     if extra_amount_paid >= total_paid_amount:
        #         pass 
        #     else:
        #         frappe.throw("Fees Refundable / Adjustable amount is more than paid amount")      
        else:
            frappe.throw("Fees Refundable / Adjustable amount is more than paid amount")    
    elif adjusted_amount ==0:
        pass
    else:
        frappe.throw("Fees Refundable / Adjustable amount is more than paid amount")    


def bank_draft_amount(self):
    if self.mode_of_payment=="Bank Draft":
        total_amount=0    
        for d in self.get("bank_draft_references"):
                total_amount=total_amount+ d.bank_draft_amount   
        if total_amount == self.paid_amount:
            pass
        elif total_amount < self.paid_amount:
            frappe.throw("Bank Draft Amount is less than Paid Amount")
        elif total_amount > self.paid_amount:
            flag="pass"
            for t in self.get('references'):
                if t.fees_category=="Fees Refundable / Adjustable":
                    flag="no_pass"
                    break 
            if flag=="pass":    
                Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']],fields=['name'])
                for t in self.get('references'):
                    reference_name=t.reference_name
                    due_date=t.due_date
                    break
                allocated_excess_amount=0
                for t in self.get('references'):
                    allocated_excess_amount=allocated_excess_amount+t.allocated_amount   
                paid_amount=allocated_excess_amount      
                allocated_excess_amount=total_amount-allocated_excess_amount  
                paid_amount=paid_amount+allocated_excess_amount
                self.total_allocated_amount=paid_amount
                self.difference_amount=paid_amount-self.total_allocated_amount 
                self.append("references",{
                "reference_doctype":"Fees",
                "fees_category":"Fees Refundable / Adjustable",
                "account_paid_from":Account[0]['name'],
                "reference_name":reference_name,
                "allocated_amount":allocated_excess_amount,
                "total_amount":allocated_excess_amount,
                "outstanding_amount":allocated_excess_amount,
                "due_date":due_date,
                "exchange_rate":1,
            }) 
            else:
                Account=frappe.db.get_all("Account",filters=[['name','like','%Fees Refundable / Adjustable%'],['account_type','=','Income Account']],fields=['name'])
                reference_name=""
                allocated_excess_amount=0
                for t in self.get('references'):
                    if t.fees_category!="Fees Refundable / Adjustable":
                        allocated_excess_amount=allocated_excess_amount+t.allocated_amount  
                paid_amount=allocated_excess_amount      
                allocated_excess_amount=total_amount-allocated_excess_amount  
                paid_amount=paid_amount+allocated_excess_amount
                self.total_allocated_amount=paid_amount
                self.difference_amount=paid_amount-self.total_allocated_amount 

                # allocated_excess_amount=Recon_info['total_allocated_amount']-allocated_excess_amount
                for t in self.get('references'):
                    reference_name=t.reference_name
                    break 
                count=0
                for t in self.get('references'):
                    # reference_name=t.reference_name
                    if t.fees_category=="Fees Refundable / Adjustable":
                        t.reference_doctype=t.reference_doctype
                        t.fees_category="Fees Refundable / Adjustable"
                        t.account_paid_from=Account[0]['name']
                        t.reference_name=reference_name
                        t.allocated_amount=allocated_excess_amount
                        t.total_amount=allocated_excess_amount
                        t.outstanding_amount=allocated_excess_amount          