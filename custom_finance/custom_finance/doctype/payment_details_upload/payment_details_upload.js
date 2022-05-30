// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Details Upload', {
	refresh: function(frm) {
		if (frm.doc.payment_status==0){
			frm.add_custom_button(__('View Fees Records'), function() {
				frappe.route_options = {
					student: frm.doc.student
				};
				frappe.set_route('List', 'Fees');
			});
		}
		if (frm.doc.payment_status==1){
			frm.add_custom_button(__('View Payment Records'), function() {
				frappe.route_options = {
					name: frm.doc.payment_id
				};
				frappe.set_route('List', 'Payment Entry');
			});
		}
}
});
