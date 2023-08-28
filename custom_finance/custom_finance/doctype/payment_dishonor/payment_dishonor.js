// Copyright (c) 2023, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Dishonor', {
	refresh: function(frm) {
        frm.set_df_property('payment_references', 'cannot_add_rows', true);
        frm.set_df_property('payment_references', 'cannot_delete_rows', true);
		if(!frm.is_new()){
			frappe.call({
				method:'custom_finance.custom_finance.doctype.payment_dishonor.payment_dishonor.get_payment_entry_record',
				args:{
					student:frm.doc.student
				},
				callback: function(result){
					const res = result.message
					let arr= []
					res.map((r) => {
						const { name } = r
						arr.push(name)	
					})
					set_field_options("payment_entry" , arr)
				}
			})
		}
		if(frm.doc.docstatus == 1){
			if (!frappe.boot.desk_settings.form_sidebar) {
				cur_page.page.page.add_action_icon("printer", function() {
					cur_frm.print_doc();
				}, '', __("Print"));
			}
		}
	},
	payment_entry: function(frm) {
		frm.trigger("payment_entry_data")
		frm.set_value("payment_references" ,"");
		if (frm.doc.payment_entry) {
			frappe.call({
				method: "custom_finance.custom_finance.doctype.payment_dishonor.payment_dishonor.get_payment_entry_child",
				args: {
					"payment_entry": frm.doc.payment_entry
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.clear_table(frm.doc, 'payment_references');
						(r.message).forEach(d => {
							var row = frm.add_child("payment_references")
							row.reference_doctype = d.reference_doctype;
							row.fees_category=d.fees_category;
							row.semester = d.semester;
							row.program = d.program;
							row.account_paid_from = d.account_paid_from;
                            row.description=d.description;
                            row.fee_structure=d.fee_structure;
                            
                            row.hostel_fee_structure=d.hostel_fee_structure;
                            row.account_paid_to=d.account_paid_to;
                            row.reference_name=d.reference_name;
                            row.due_date=d.due_date;
							row.total_amount=d.total_amount;
							row.outstanding_amount=d.outstanding_amount;
							row.allocated_amount=d.allocated_amount;
						});
						frm.refresh_field("payment_references")
					}
				}
			});
			frm.set_value("bank_draft_references" ,"");
			frappe.call({
				method: "custom_finance.custom_finance.doctype.payment_dishonor.payment_dishonor.get_bank_draft_references",
				args: {
					"payment_entry": frm.doc.payment_entry
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.clear_table(frm.doc, 'bank_draft_references');
						(r.message).forEach(d => {
							var row = frm.add_child("bank_draft_references")
							row.chequereference_no = d.chequereference_no;
							row.chequereference_date=d.chequereference_date;
							row.bank_draft_amount = d.bank_draft_amount;
							row.bank_name = d.bank_name;
						});
						frm.refresh_field("bank_draft_references")
					}
				}
			});
		}
	},
	student:function(frm){
		let arr = []
		frappe.call({
			method:'custom_finance.custom_finance.doctype.payment_dishonor.payment_dishonor.get_payment_entry_record',
			args:{
				student:frm.doc.student
			},
			callback: function(result){
				const res = result.message
				res.map((r) => {
					const { name } = r
					arr.push(name)
				})
				set_field_options("payment_entry" , arr)
			}
		})
	},
	payment_entry_data(frm){
		if (frm.doc.payment_entry) {
			console.log(frm.doc.payment_entry);
			frappe.call({
				method: "custom_finance.custom_finance.doctype.payment_dishonor.payment_dishonor.get_payment_entry",
				args: {
					"payment_entry": frm.doc.payment_entry
				},
				callback: function(r) {
					if(r){
                        var info=r.message
						console.log();
						frm.doc.posting_date=info[0].posting_date
						frm.doc.mode_of_payment=info[0].mode_of_payment
						frm.doc.students=info[0].student
						frm.doc.student_name=info[0].party_name
						frm.doc.roll_no=info[0].roll_no
						frm.doc.sams_portal_id=info[0].sams_portal_id
						frm.doc.permanent_registration_number=info[0].permanent_registration_number
						frm.doc.student_email=info[0].student_email
						frm.doc.paid_amount=info[0].paid_amount
						frm.doc.reference_no=info[0].reference_no
						frm.doc.reference_date=info[0].reference_date
						frm.refresh();
					}
				}
			});
		}
	}
});
