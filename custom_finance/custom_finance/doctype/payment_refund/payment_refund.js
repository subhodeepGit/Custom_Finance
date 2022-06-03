// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Refund', {
	onload: function(frm) {
		frm.set_query("account_paid_from","references", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'name': "Fees Refundable / Adjustable - KP",
				}
			};
		});
		frm.set_query("fees_category","references", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'name': "Fees Refundable / Adjustable",
				}
			};
		});
	}
});

frappe.ui.form.on("Payment Refund","mode_of_payment", function(frm){
		frappe.call({
			method: "custom_finance.custom_finance.doctype.payment_refund.payment_refund.paid_from_fetch",								
			args: {
					mode_of_payment: frm.doc.mode_of_payment,
					company: frm.doc.company
			},
			callback: function(r) {
				var res=r.message;
				frm.set_value("paid_from",res);
			}
		});
});

frappe.ui.form.on("Payment Entry Reference Refund","allocated_amount", function(frm, cdt, cdn){
	var d=locals[cdt][cdn];
		d.total_amount=d.allocated_amount;
		refresh_field("total_amount", d.name, d.parentfield);
});



