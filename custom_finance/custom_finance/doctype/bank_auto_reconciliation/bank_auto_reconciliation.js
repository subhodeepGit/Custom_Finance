// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Auto Reconciliation Child', {
	"paying_tuition_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_oustanding_tuition_fees=d.total_outstanding_tuition_fees-d.paying_tuition_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_oustanding_tuition_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_development_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_development_fees=d.total_outstanding_development_fees-d.paying_development_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_development_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_other_institutional_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_other_institutional_fees=d.total_outstanding_other_institutional_fees-d.paying_other_institutional_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_other_institutional_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_miscellaneous_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_miscellaneous_fees=d.total_outstanding_miscellaneous_fees-d.paying_miscellaneous_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_miscellaneous_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_examination_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_examination_fees=d.total_outstanding_examination_fees-d.paying_examination_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_examination_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_transportation_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_transportation_fees=d.total_outstanding_transportation_fees-d.paying_transportation_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_transportation_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_counselling_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_counselling_fees=d.total_outstanding_counselling_fees-d.paying_counselling_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_counselling_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_re_admission_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_re_admission_fees=d.total_outstanding_re_admission_fees-d.paying_re_admission_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_re_admission_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_arrear_dues": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_arrear_dues=d.total_outstanding_arrear_dues-d.paying_arrear_dues
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_arrear_dues", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_hostel_admission_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_hostel_admission_fees=d.total_outstanding_hostel_admission_fees-d.paying_hostel_admission_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_hostel_admission_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_hostel_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_hostel_fees=d.total_outstanding_hostel_fees-d.paying_hostel_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_hostel_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_mess_fees": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.current_outstanding_mess_fees=d.total_outstanding_mess_fees-d.paying_mess_fees
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("current_outstanding_mess_fees", d.name, d.parentfield);
		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
	"paying_fees_refundable__adjustable": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.total_paying_amount=d.paying_tuition_fees+d.paying_development_fees+d.paying_other_institutional_fees+d.paying_miscellaneous_fees+d.paying_examination_fees+d.paying_transportation_fees+d.paying_counselling_fees+d.paying_re_admission_fees+d.paying_arrear_dues+d.paying_hostel_admission_fees+d.paying_hostel_fees+d.paying_mess_fees+d.paying_fees_refundable__adjustable

		refresh_field("total_paying_amount", d.name, d.parentfield);
	},
});

frappe.ui.form.on('Bank Auto Reconciliation', {
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
			method: "custom_finance.custom_finance.doctype.bank_auto_reconciliation.bank_auto_reconciliation.get_fees",                
			args: {
				"date": frm.doc.data_of_clearing,
				"type_of_transaction":frm.doc.type_of_transaction
			},
			callback: function(r) {
				if(r.message){
					if(frm.doc.type_of_transaction !="Online Payment"){
						frappe.model.clear_table(frm.doc, 'student_reference');
						(r.message).forEach(element => {
							var c = frm.add_child("student_reference")
							c.student=element.student
							c.student_name=element.student_name
							c.utr_no=element.unique_transaction_reference_utr
							c.amount=element.amount
							c.outstanding_amount=element.outstanding_amount
							c.total_paying_amount=element.paying_re_admission_fees+element.paying_arrear_dues+element.paying_tuition_fees+element.paying_development_fees+element.paying_hostel_admission_fees+element.paying_counselling_fees+element.paying_examination_fees+element.paying_transportation_fees+element.paying_mess_fees+element.paying_miscellaneous_fees+element.paying_hostel_fees+element.paying_other_institutional_fees+element.paying_fees_refundable__adjustable
							c.reconciliation_status=element.reconciliation_status
							c.remarks=element.remarks
							c.total_outstanding_re_admission_fees=element.re_admission_fees
							c.current_outstanding_re_admission_fees=c.total_outstanding_re_admission_fees-element.paying_re_admission_fees					
							c.total_outstanding_arrear_dues=element.arrear_dues
							c.current_outstanding_arrear_dues=c.total_outstanding_arrear_dues-element.paying_arrear_dues
							c.total_outstanding_tuition_fees=element.tuition_fees
							c.current_oustanding_tuition_fees=c.total_outstanding_tuition_fees-element.paying_tuition_fees
							c.total_outstanding_development_fees=element.development_fees
							c.current_outstanding_development_fees=c.total_outstanding_development_fees-element.paying_development_fees
							c.total_outstanding_hostel_admission_fees=element.hostel_admission_fees
							c.current_outstanding_hostel_admission_fees=c.total_outstanding_hostel_admission_fees-element.paying_hostel_admission_fees
							c.total_outstanding_counselling_fees=element.counselling_fees
							c.current_outstanding_counselling_fees=c.total_outstanding_counselling_fees-element.paying_counselling_fees
							c.total_outstanding_examination_fees=element.examination_fees
							c.current_outstanding_examination_fees=c.total_outstanding_examination_fees-element.paying_examination_fees
							c.total_outstanding_transportation_fees=element.transportation_fees
							c.current_outstanding_transportation_fees=c.total_outstanding_transportation_fees-element.paying_transportation_fees
							c.total_outstanding_mess_fees=element.mess_fees
							c.current_outstanding_mess_fees=c.total_outstanding_mess_fees-element.paying_mess_fees
							c.total_outstanding_miscellaneous_fees=element.miscellaneous_fees
							c.current_outstanding_miscellaneous_fees=c.total_outstanding_miscellaneous_fees-element.paying_miscellaneous_fees
							c.total_outstanding_hostel_fees=element.hostel_fees
							c.current_outstanding_hostel_fees=c.total_outstanding_hostel_fees-element.paying_hostel_fees
							c.total_outstanding_other_institutional_fees=element.other_institutional_fees
							c.current_outstanding_other_institutional_fees=c.total_outstanding_other_institutional_fees-element.paying_other_institutional_fees
							
							c.paying_re_admission_fees=element.paying_re_admission_fees
							c.paying_arrear_dues=element.paying_arrear_dues
							c.paying_tuition_fees=element.paying_tuition_fees
							c.paying_development_fees=element.paying_development_fees
							c.paying_hostel_admission_fees=element.paying_hostel_admission_fees
							c.paying_counselling_fees=element.paying_counselling_fees
							c.paying_examination_fees=element.paying_examination_fees
							c.paying_transportation_fees=element.paying_transportation_fees
							c.paying_mess_fees=element.paying_mess_fees
							c.paying_miscellaneous_fees=element.paying_miscellaneous_fees
							c.paying_hostel_fees=element.paying_hostel_fees
							c.paying_other_institutional_fees=element.paying_other_institutional_fees
							c.paying_fees_refundable__adjustable=element.paying_fees_refundable__adjustable
						});
					};
					if(frm.doc.type_of_transaction=="Online Payment"){
						frappe.model.clear_table(frm.doc, 'student_reference');
						(r.message).forEach(element => {
							var c = frm.add_child("student_reference")
							c.student=element.party
							c.student_name=element.party_name
							c.utr_no=element.transaction_id
							c.amount=element.paying_amount
							c.outstanding_amount=element.outstanding_amount
							c.total_paying_amount=element.paying_re_admission_fees+element.paying_arrear_dues+element.paying_tuition_fees+element.paying_development_fees+element.paying_hostel_admission_fees+element.paying_counselling_fees+element.paying_examination_fees+element.paying_transportation_fees+element.paying_mess_fees+element.paying_miscellaneous_fees+element.paying_hostel_fees+element.paying_other_institutional_fees+element.paying_fees_refundable__adjustable
							c.reconciliation_status=element.payment_status
							c.remarks=element.remarks
							c.current_outstanding_re_admission_fees=c.total_outstanding_re_admission_fees=element.re_admission_fees
							c.current_outstanding_arrear_dues=c.total_outstanding_arrear_dues=element.arrear_dues
							c.current_oustanding_tuition_fees=c.total_outstanding_tuition_fees=element.tuition_fees
							c.current_outstanding_development_fees=c.total_outstanding_development_fees=element.development_fees
							c.current_outstanding_hostel_admission_fees=c.total_outstanding_hostel_admission_fees=element.hostel_admission_fees
							c.current_outstanding_counselling_fees=c.total_outstanding_counselling_fees=element.counselling_fees
							c.current_outstanding_examination_fees=c.total_outstanding_examination_fees=element.examination_fees
							c.current_outstanding_transportation_fees=c.total_outstanding_transportation_fees=element.transportation_fees
							c.current_outstanding_mess_fees=c.total_outstanding_mess_fees=element.mess_fees
							c.current_outstanding_miscellaneous_fees=c.total_outstanding_miscellaneous_fees=element.miscellaneous_fees
							c.current_outstanding_hostel_fees=c.total_outstanding_hostel_fees=element.hostel_fees
							c.current_outstanding_other_institutional_fees=c.total_outstanding_other_institutional_fees=element.other_institutional_fees

							c.paying_re_admission_fees=element.paying_re_admission_fees
							c.paying_arrear_dues=element.paying_arrear_dues
							c.paying_tuition_fees=element.paying_tuition_fees
							c.paying_development_fees=element.paying_development_fees
							c.paying_hostel_admission_fees=element.paying_hostel_admission_fees
							c.paying_counselling_fees=element.paying_counselling_fees
							c.paying_examination_fees=element.paying_examination_fees
							c.paying_transportation_fees=element.paying_transportation_fees
							c.paying_mess_fees=element.paying_mess_fees
							c.paying_miscellaneous_fees=element.paying_miscellaneous_fees
							c.paying_hostel_fees=element.paying_hostel_fees
							c.paying_other_institutional_fees=element.paying_other_institutional_fees
							c.paying_fees_refundable__adjustable=element.paying_fees_refundable__adjustable

						});
					};
				}
				frm.refresh();
				frm.refresh_field("student_reference")
			}
		})
	}
	
});
frappe.ui.form.on('Bank Auto Reconciliation', {
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
