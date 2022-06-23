// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Auto Reconciliation', {
	onload: function(frm) {
		frm.set_df_property('student_reference', 'cannot_add_rows', true);
		frm.set_df_property('student_reference', 'cannot_delete_rows', true);
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
