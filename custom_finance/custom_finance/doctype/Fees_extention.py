import frappe
from frappe.model.mapper import get_mapped_doc
from ed_tec.ed_tec.utils import duplicate_row_validation

def on_submit(self,method):
    child_table_fees_outsatnding(self)

def child_table_fees_outsatnding(self):
    ### payment entry child doc
    s=self.get("references")[0]
    #####
    ### fees child doc
    ref_details=frappe.get_all("Fee Component",{"parent":s.reference_name},["name","grand_fee_amount","outstanding_fees","fees_category"])
    #####
    for d in self.get("references"):
        if d.allocated_amount:
            for t in ref_details:
                if t['fees_category']==d.fees_category:
                    frappe.db.set_value("Fee Component",t['name'], "outstanding_fees",d.outstanding_amount)

