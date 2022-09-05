// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('ICICI Online Payment', {
	party: function(frm) {
		frappe.call({
			method:"custom_finance.custom_finance.doctype.icici_online_payment.icici_online_payment.get_outstanding_amount",
			args: {
				student: frm.doc.party
			},
			callback: function(r){
				if(r.message){
					var result = r.message;
					frm.set_value("total_outstanding_amout",result);
					frm.set_value("paying_amount",result);
				}
			}
		})
	}
});
