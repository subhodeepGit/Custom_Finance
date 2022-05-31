frappe.listview_settings['Payment Details Upload'] = {
	add_fields: ["reconciliation_status"],
	get_indicator: function(doc) {
        if(doc.reconciliation_status==1) {
				if (doc.payment_status==0){
            		return [__("Matched (Reconciled) not paid"), "orange"];
				} else if (doc.payment_status==1){
					return [__("Matched (Reconciled) and paid"), "green"];
				}

            } else if (doc.reconciliation_status==0) {
                	return [__("Not-Matched (Not-Reconciled)"), "red"];
                }
	}
};