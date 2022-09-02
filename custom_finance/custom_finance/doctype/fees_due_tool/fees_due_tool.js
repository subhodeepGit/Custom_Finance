// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

// Fetch all student data whose fees is due
frappe.ui.form.on('Fees Due Tool', {
	get_students:function(frm){
			frm.clear_table("studentss");
			frappe.call({
				method: "custom_finance.custom_finance.doctype.fees_due_tool.fees_due_tool.get_students",
				args:{
					programs: frm.doc.programs,
					program: frm.doc.program,
					academic_term: frm.doc.academic_term,
					academic_year: frm.doc.academic_year,
	
				},
			
				callback: function(r) {
					if(r.message){
                        frappe.model.clear_table(frm.doc, 'studentss');
                        (r.message).forEach(element => {
                            var c = frm.add_child("studentss")
                            c.fees_id=element.name
                            c.students=element.student
                            c.student_name=element.student_name
							c.student_email_id=element.student_email
							c.outstanding_amounts=element.outstanding_amount
                        });
                    } 
                    frm.refresh();
                    frm.refresh_field("studentss")
				}
			});	
	}	
});
frappe.ui.form.on("Fees Due Tool", {
	// Filter semester according to program
	setup:function(frm){
		frm.set_query("program", function() {
			return {
				filters: {
					"programs":frm.doc.programs	
				}
			};
		});
	},
	// Bulk Email For Student
    refresh:function(frm){
		if(cur_frm.doc.studentss && frm.doc.email_to=="Student"){
			if((cur_frm.doc.studentss).length!=0 && frm.doc.docstatus===1){
				frm.add_custom_button(__("Bulk Email","View"), function() {
					frappe.call({
						method: 'custom_finance.custom_finance.doctype.fees_due_tool.fees_due_tool.get_student_emails',
						args: {
							studentss: frm.doc.studentss
						},
						
						callback: function(resp){
							if(resp.message){
								new frappe.views.CommunicationComposer({
								
									doc: cur_frm.doc,
									frm: cur_frm,
									// subject: __(cur_frm.meta.name) + ': ' + cur_frm.docname,
									subject: "Fees is Due",
									recipients:resp.message, 
									attach_document_print: false,
							});
							}
						}
					})
				});
			}
		}
	}
});
frappe.ui.form.on("Fees Due Tool", {
	refresh:function(frm){
		// Bulk Email For Guardian
		if(cur_frm.doc.studentss && frm.doc.email_to=="Guardian"){
			if((cur_frm.doc.studentss).length!=0 && frm.doc.docstatus===1){
				frm.add_custom_button(__("Bulk Email","View"), function() {
					frappe.call({
						method: 'custom_finance.custom_finance.doctype.fees_due_tool.fees_due_tool.get_guardian_emails',
						args: {
							studentss: frm.doc.studentss
						},
						
						callback: function(resp){
							if(resp.message){
								new frappe.views.CommunicationComposer({
								
									doc: cur_frm.doc,
									frm: cur_frm,
									subject: "Fees is Due",
									recipients:resp.message, 
									attach_document_print: false,
							});
							}
						}
					})
				});
			}
		}
	}
});
frappe.ui.form.on("Fees Due Tool", {
	refresh:function(frm){
		// Bulk Email For Both
		if(cur_frm.doc.studentss && frm.doc.email_to=="Both"){
			if((cur_frm.doc.studentss).length!=0 && frm.doc.docstatus===1){
				frm.add_custom_button(__("Bulk Email","View"), function() {
					frappe.call({
						method: 'custom_finance.custom_finance.doctype.fees_due_tool.fees_due_tool.get_both_emails',
						args: {
							studentss: frm.doc.studentss
						},
						
						callback: function(resp){
							if(resp.message){
								new frappe.views.CommunicationComposer({
								
									doc: cur_frm.doc,
									frm: cur_frm,
									subject: "Fees is Due",
									recipients:resp.message, 
									attach_document_print: false,
							});
							}
						}
					})
				});
			}
		}
	}
});
	

frappe.ui.form.on("Fees Due Tool", {
	onload:function(frm){
		//cannot able to add rows
		frm.set_df_property("studentss", "cannot_add_rows", true);
	}
});