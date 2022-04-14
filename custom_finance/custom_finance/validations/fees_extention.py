from typing_extensions import Self
import frappe

def validate(self,method):
    calucate_total(self)
    if self.mode_of_payment=="NEFT" or self.mode_of_payment=="RTGS" or self.mode_of_payment=="IMPS":
        if self.reference_no==None:
            frappe.throw("Reference UTR No. not maintaned")
        else:
            Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":self.reference_no,"type_of_transaction":self.mode_of_payment},
                                        ["name","amount","total_allocated_amount","date","party_name"])
            if len(Recon_info)!=0:
                Recon_info=Recon_info[0]
                if Recon_info["party_name"]==None:
                    if Recon_info['total_allocated_amount']>0:
                        if Recon_info['total_allocated_amount']>=self.total_allocated_amount:
                            self.reference_date=Recon_info['date'] 
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
    allocation_amount(self)                      

def on_submit(self,method):
    child_table_fees_outsatnding(self)
    if self.mode_of_payment=="NEFT" or self.mode_of_payment=="RTGS" or self.mode_of_payment=="IMPS":
        
        Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":self.reference_no,"type_of_transaction":self.mode_of_payment},
                                ["name","amount","total_allocated_amount","date","count"])                     
        Recon_info=Recon_info[0]
        Grant_total_amount=Recon_info['total_allocated_amount']-self.total_allocated_amount
        count=int(Recon_info["count"])+1
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"total_allocated_amount",Grant_total_amount)
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"party_name",self.party)
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"count",count)   

def on_cancel(self,method):
    child_table_fees_outsatnding(self)
    if self.mode_of_payment=="NEFT" or self.mode_of_payment=="RTGS" or self.mode_of_payment=="IMPS":
        Recon_info=frappe.get_all("Bank Reconciliation Statement",{"unique_transaction_reference_utr":self.reference_no,"type_of_transaction":self.mode_of_payment},
                                ["name","amount","total_allocated_amount","date","count"])
        Recon_info=Recon_info[0]  
        if Recon_info["count"]==1:
            frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"party_name","")
        Grant_total_amount=Recon_info['total_allocated_amount']+self.total_allocated_amount  
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"total_allocated_amount",Grant_total_amount) 
        count=int(Recon_info["count"])-1
        frappe.db.set_value("Bank Reconciliation Statement",Recon_info['name'],"count",count)  

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
    allocated_amount=[]
    for d in self.get("references"):
        allocated_amount.append(d.allocated_amount)
    self.paid_amount=abs(sum(allocated_amount))

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
