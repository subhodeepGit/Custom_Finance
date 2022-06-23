// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fees Due Tool', {
	get_students:function(frm){
		alert("hello")
			frm.clear_table("studentss");
			frappe.call({
				method: "custom_finance.custom_finance.doctype.fees_due_tool.fees_due_tool.get_students",
				// /opt/bench/frappe-bench/apps/custom_finance/custom_finance/custom_finance/doctype/fees_due_tool/fees_due_tool.py
				args:{
					programs: frm.doc.programs,
					program: frm.doc.program,
					academic_term: frm.doc.academic_term,
					academic_year: frm.doc.academic_year,
	
				},
			
				callback: function(r) {
					alert(r.message)
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
