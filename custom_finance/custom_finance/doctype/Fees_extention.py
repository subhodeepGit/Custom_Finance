import frappe
from frappe.model.mapper import get_mapped_doc
from ed_tec.ed_tec.utils import duplicate_row_validation

def on_submit(self,method):
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

