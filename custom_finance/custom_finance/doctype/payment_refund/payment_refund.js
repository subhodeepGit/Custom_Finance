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
	},

	refresh: function(frm) {
		erpnext.toggle_naming_series();

		if(frm.doc.docstatus > 0) {
			frm.add_custom_button(__('Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.jv_entry_voucher_no,
					"from_date": frm.doc.posting_date,
					"to_date": moment(frm.doc.modified).format('YYYY-MM-DD'),
					"company": frm.doc.company,
					"finance_book": frm.doc.finance_book,
					"group_by": '',
					"show_cancelled_entries": frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "General Ledger");
			}, __('View'));
		}
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

frappe.ui.form.on("Payment Entry Reference Refund", "fees_category", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var a=0;
    if (d.fees_category){
        a=frm.doc.references.length;
        frm.set_value("count_rows", a);
        if(a>=1){
            frm.set_df_property('references', 'cannot_add_rows', true);
            frm.set_df_property('references', 'cannot_delete_rows', true);
        }
    }
});


