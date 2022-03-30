from typing_extensions import Self
import frappe
from frappe.model.mapper import get_mapped_doc
from ed_tec.ed_tec.utils import duplicate_row_validation
from frappe.utils import flt

def validate(self,method):
    calucate_total(self)

def on_submit(self,method):
    child_table_fees_outsatnding(self)

def on_cancel(self,method):
    child_table_fees_outsatnding(self)  

def child_table_fees_outsatnding(self):
    ### payment entry child doc
    # s=self.get("references")[0]
    z=self.get("references")
    reference_name=[]
    for i in z:
        reference_name.append(i.reference_name)
    reference_name = list(set(reference_name))    
    #####
    ### fees child doc
    Outstanding_amount=[]
    for v in reference_name:
        # ref_details=frappe.get_all("Fee Component",{"parent":s.reference_name},["name","grand_fee_amount","outstanding_fees","fees_category"])
        # ref_details=frappe.get_all("Fee Component",{"parent":v},["name","grand_fee_amount","outstanding_fees","fees_category"])
        #####
        for d in self.get("references"):
            if d.allocated_amount:
                ref_details=frappe.get_all("Fee Component",{"parent":v,"fees_category":d.fees_category},["name","grand_fee_amount","outstanding_fees","fees_category"])
                for t in ref_details:
                    if t['fees_category']==d.fees_category:
                        Outstanding_amount.append(d.outstanding_amount)
                        frappe.db.set_value("Fee Component",t['name'], "outstanding_fees",d.outstanding_amount)
        frappe.db.set_value("Fees",v, "outstanding_amount",sum(Outstanding_amount))
        Outstanding_amount=[]

def calucate_total(self):
    allocated_amount=[]
    for d in self.get("references"):
        # allocated_amount=flt(d.allocated_amount)
        allocated_amount.append(d.allocated_amount)
    self.paid_amount=sum(allocated_amount)