frappe.listview_settings['ICICI Online Payment'] = {
	add_fields: ["payment_status"],
	get_indicator: function(doc) {
        if(doc.transaction_status=="SUCCESS") {
				if (doc.payment_status==0){
            		return [__("Transaction successful but money receipt not generated"), "orange"];
				} else if (doc.payment_status==1){
					return [__("Transaction successful and money receipt generated"), "green"];
				}

            } else if (doc.transaction_status=="FAILED") {
                	return [__("Transaction Failed"), "red"];
                }
	}
};