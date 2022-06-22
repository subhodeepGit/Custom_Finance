// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Auto Reconciliation', {
	get_studnet: function(frm) {
		alert("ok")
		frm.clear_table("student_reference");
		frappe.call({
			method: "custom_finance.custom_finance.doctype.auto_reconciliation.auto_reconciliation.get_fees",                
			args: {
				"date": frm.doc.data_of_clearing,
				"type_of_transaction":frm.doc.type_of_transaction
			},
			// callback: function(r) {
			// 	if(r.message){
			// 		var utr=r.message;
			// 		frm.set_value("reference_no",utr)
			// 	}
			// }
		})
	}
});
