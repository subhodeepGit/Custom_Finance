frappe.ui.form.on('Fee Schedule',{
    setup: function(frm) {
        frm.set_query("academic_term", function() {
            return {
                filters: {
                    "academic_year":frm.doc.academic_year
                }
            };
        });
        frm.set_query("program", function() {
            return {
                filters: {
                    "programs":frm.doc.programs
                }
            };
        });
    },
    refresh:function(frm){
        frm.set_query("student_group","student_groups", function() {
            return {
                filters: {
                    "program":frm.doc.program
                }
            };
        });
        if (frm.doc.fee_creation_status === 'Successful') {
			frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					// voucher_no: frm.doc.name,
                    voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: '',
					show_cancelled_entries: frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "Fee structure General Ledger");
                // frappe.set_route("query-report", "General Ledger");
                
			});
		}
    }
})
frappe.ui.form.on('Fee Schedule', {
    refresh:function(frm) {
		if(frappe.user.has_role(["Accounts User","Student","Education Administrator"]) && !frappe.user.has_role(["Administrator"])){
  			frm.remove_custom_button('Create Fees');
        }
	}
}


);