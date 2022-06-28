// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Reconciliation Statement', {
	refresh: function(frm) {
		if (frm.doc.docstatus==1 && frm.doc.party_name!=undefined){
			frm.add_custom_button(__('View Payment Entry Records'), function() {
				frappe.route_options = {
					reference_no: frm.doc.unique_transaction_reference_utr
				};
				frappe.set_route('List', 'Payment Entry');
			});
		}
		if (frm.doc.docstatus==1 && frm.doc.party_name!=undefined){
			frm.add_custom_button(__('View Surplus Payment Entry Records'), function() {
				frappe.route_options = {
					reference_no: frm.doc.unique_transaction_reference_utr
				};
				frappe.set_route('List', 'Payment Refund');
			});
		}
	}
});
