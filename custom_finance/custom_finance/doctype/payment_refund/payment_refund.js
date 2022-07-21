// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Refund', {
	onload: function(frm) {
		frm.set_df_property('references', 'cannot_add_rows', true);
		frm.set_df_property('references', 'cannot_delete_rows', true);
		frm.set_query("account_paid_from","references", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'name': "Fees Refundable / Adjustable - KP",
				}
			};
		});
		frm.set_query("account_paid_to","references", function(_doc, cdt, cdn) {
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
		frm.set_query("mode_of_payment", function(_doc, cdt, cdn) {
			return {
				filters: {
					'is_refundable_or_adjustable': 1,
				}
			};
		});
	},
	payment_type: function(frm) {
		if (frm.doc.payment_type == "Receive"){	
			var df = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_from", frm.doc.name);
			df.read_only = 1
			df.reqd = 0
			frm.clear_table("references");
			frm.refresh_field('references');
			frm.refresh_field('account_paid_to');
			frm.refresh_field('account_paid_from');
			frm.set_df_property('references', 'cannot_add_rows', false);
            frm.set_df_property('references', 'cannot_delete_rows', false);
			var df1 = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_to", frm.doc.name);
			df1.read_only = 0
			df1.reqd = 1		
			frm.clear_table("references");
			frm.refresh_field('references');
			frm.refresh_field('account_paid_to');
			frm.refresh_field('account_paid_from');
			frm.set_df_property('references', 'cannot_add_rows', false);
            frm.set_df_property('references', 'cannot_delete_rows', false);
		} else if (frm.doc.payment_type == "Pay"){
			var df = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_to", frm.doc.name);
			df.read_only = 1
			df.reqd = 0
			frm.clear_table("references");
			frm.refresh_field('references');
			frm.refresh_field('account_paid_to');
			frm.refresh_field('account_paid_from');
			frm.set_df_property('references', 'cannot_add_rows', false);
            frm.set_df_property('references', 'cannot_delete_rows', false);
			var df1 = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_from", frm.doc.name);
			df1.read_only = 0
			df1.reqd = 1	
			frm.clear_table("references");
			frm.refresh_field('references');
			frm.refresh_field('account_paid_to');
			frm.refresh_field('account_paid_from');
			frm.set_df_property('references', 'cannot_add_rows', false);
            frm.set_df_property('references', 'cannot_delete_rows', false);
		}
		else if (frm.doc.payment_type == ""){
			frm.clear_table("references");
			frm.refresh_field('references');
			frm.refresh_field('account_paid_to');
			frm.refresh_field('account_paid_from');
			frm.set_df_property('references', 'cannot_add_rows', true);
            frm.set_df_property('references', 'cannot_delete_rows', true);
		}
	},
	after_save: function(frm) {
		if (frm.doc.payment_type == "Receive"){
			var df = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_from", frm.doc.name);
			df.read_only = 1
			df.reqd = 0
			var df1 = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_to", frm.doc.name);
			df1.read_only = 0
			df1.reqd = 1
		} else if (frm.doc.payment_type == "Pay"){
			var df = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_to", frm.doc.name);
			df.read_only = 1
			df.reqd = 0
			var df1 = frappe.meta.get_docfield("Payment Entry Reference Refund","account_paid_from", frm.doc.name);
			df1.read_only = 0
			df1.reqd = 1
		}

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
	},
	mode_of_payment: function(frm) {
		if(frm.doc.mode_of_payment==("RTGS"||"NEFT"||"IMPS")) {
			frappe.call({
				method: "custom_finance.custom_finance.doctype.payment_details_upload.payment_details_upload.utr_callback",                
				args: {
					"party": frm.doc.party,
					"mode_of_payment": frm.doc.mode_of_payment
				},
				callback: function(r) {
					if(r.message){
						var utr=r.message;
						frm.set_value("reference_no",utr)
					}
				}
			});
		}
	},
	company: function(frm) {
		frappe.call({
            method: "custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_cost_center",
            callback: function(r) { 
                if (r.message){
                    frm.set_value("cost_center",r.message)
                }
            } 
            
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
				if(frm.doc.payment_type == "Pay"){
					frm.set_value("paid_from",null);
					frm.set_value("paid_from_account_type",null);
					// frm.set_value("paid_from_account_currency",null);
					frm.set_value("paid_to",res);
				}
				else if(frm.doc.payment_type == "Receive"){
					frm.set_value("paid_to",null);
					frm.set_value("paid_to_account_type",null);
					// frm.set_value("paid_to_account_currency",null);
					frm.set_value("paid_from",res);
				}
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

frappe.ui.form.on("Payment Refund","reference_no", function(frm){
	if(frm.doc.mode_of_payment=="IMPS" || frm.doc.mode_of_payment=="RTGS" || frm.doc.mode_of_payment=="NEFT" ){
		frappe.call({
			method: "custom_finance.custom_finance.validations.online_fees.paid_from_account_type",								
			args: {
					reference_no:frm.doc.reference_no,
					mode_of_payment:frm.doc.mode_of_payment,
			},
			callback: function(r) {
				var res=r.message;
				frm.set_value("reference_date",res);
			}
		});
	}

});
frappe.ui.form.on("Payment Refund","mode_of_payment", function(frm){
    var mop = frm.doc.mode_of_payment
    if(mop == "Bank Draft"){
        frm.doc.reference_no = "Bank Draft"
        frm.set_value("reference_no",frm.doc.reference_no)
        frm.set_value("reference_date", frappe.datetime.nowdate());
        frm.refresh();
    };
	if(frm.doc.mode_of_payment == "Cash"){
		frm.set_df_property('references', 'cannot_add_rows', true);
		frm.set_df_property('references', 'cannot_delete_rows', true);
	}	 else if(frm.doc.mode_of_payment !="Cash"){
		frm.set_df_property('references', 'cannot_add_rows', false);
		frm.set_df_property('references', 'cannot_delete_rows', false);
	}
})
frappe.ui.form.on("Payment Refund","mode_of_payment", function(frm){
    var mop = frm.doc.mode_of_payment
    if(mop == "Online Payment"){
        frm.doc.reference_no = "Online Payment"
        frm.set_value("reference_no",frm.doc.reference_no)
        frm.set_value("reference_date", frappe.datetime.nowdate());
        frm.refresh();
    };
});
