// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Auto Reconciliation', {
	onload: function(frm) {
		frm.set_df_property('student_reference', 'cannot_add_rows', true);
		// frm.set_df_property('student_reference', 'cannot_delete_rows', true);
		frappe.realtime.on('fee_schedule_progress', function(data) {
			if (data.reload && data.reload === 1) {
				frm.reload_doc();
			}
			if (data.progress) {
				let progress_bar = $(cur_frm.dashboard.progress_area.body).find('.progress-bar');
				if (progress_bar) {
					$(progress_bar).removeClass('progress-bar-danger').addClass('progress-bar-success progress-bar-striped');
					$(progress_bar).css('width', data.progress+'%');
				}
			}
		});
	},
	get_studnet: function(frm) {
		frm.clear_table("student_reference");
		frappe.call({
			method: "custom_finance.custom_finance.doctype.auto_reconciliation.auto_reconciliation.get_fees",                
			args: {
				"date": frm.doc.data_of_clearing,
				"type_of_transaction":frm.doc.type_of_transaction
			},
			callback: function(r) {
				// alert(r.message)
				if(r.message){
					frappe.model.clear_table(frm.doc, 'student_reference');
					(r.message).forEach(element => {
						var c = frm.add_child("student_reference")
						c.student=element.student
						c.student_name=element.student_name
						c.utr_no=element.unique_transaction_reference_utr
						c.amount=element.amount
						c.outstanding_amount=element.outstanding_amount
						c.reconciliation_status=element.reconciliation_status
						c.remarks=element.remarks
					});
				}
				frm.refresh();
				frm.refresh_field("student_reference")
			}
		})
	}
	
});
frappe.ui.form.on('Auto Reconciliation', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1 && !frm.doc.payment_status || frm.doc.payment_status === 'Failed') {
			// if (frm.doc.docstatus === 1 ) {	
			frm.add_custom_button(__('Create Payment Entry'), function() {
				frappe.call({
					method: 'create_payment_entry',
					doc: frm.doc,
					callback: function() {
						frm.refresh();
					}
				});
			}).addClass('btn-primary');;
		}
	}
})
