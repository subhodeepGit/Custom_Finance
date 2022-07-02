frappe.listview_settings['Auto Reconciliation'] = {
	add_fields: ["payment_status", "due_date", "grand_total"],
	get_indicator: function(doc) {
		if (doc.payment_status=="Successful") {
			return [__("Fee Created"), "blue", "fee_creation_status,=,Successful"];
		} else if(doc.payment_status == "In Process") {
			return [__("Creating Fees"), "orange", "fee_creation_status,=,In Process"];
		} else if(doc.payment_status == "Failed") {
			return [__("Fee Creation Failed"), "red", "fee_creation_status,=,Failed"];
		} else {
			return [__("Fee Creation Pending"), "green", "fee_creation_status,=,"];
		}
	}
};