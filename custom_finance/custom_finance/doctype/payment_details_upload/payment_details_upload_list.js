frappe.listview_settings['Payment Details Upload'] = {
	add_fields: ["reconciliation_status"],
	get_indicator: function(doc) {
        if(doc.reconciliation_status==1) {
            	return [__("Matched (Reconciled)"), "green"];
            } else if (doc.reconciliation_status==0) {
                	return [__("Not-Matched (Not-Reconciled)"), "orange", "outstanding_amount,>,0|due_date,>,Today"];
                }
	}
};