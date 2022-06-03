///////////////////////////////////////
// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.provide("erpnext.accounts.dimensions");

frappe.ui.form.on("Program Enrollment", {
	setup: function(frm) {
		frm.add_fetch("fee_structure", "receivable_account", "receivable_account");
		frm.add_fetch("fee_structure", "income_account", "income_account");
		frm.add_fetch("fee_structure", "cost_center", "cost_center");
	},

	company: function(frm) {
		erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
	},

	onload: function(frm) {
		frm.set_query("academic_term", function() {
			return{
				"filters": {
					"academic_year": (frm.doc.academic_year)
				}
			};
		});
		frm.set_query("fee_structure", function() {
			return{
				"filters":{
					"academic_year": (frm.doc.academic_year)
				}
			};
		});
		frm.set_query("receivable_account", function(doc) {
			return {
				filters: {
					'account_type': 'Receivable',
					'is_group': 0,
					'company': doc.company
				}
			};
		});
		frm.set_query("income_account", function(doc) {
			return {
				filters: {
					'account_type': 'Income Account',
					'is_group': 0,
					'company': doc.company
				}
			};
		});
		if (!frm.doc.posting_date) {
			frm.doc.posting_date = frappe.datetime.get_today();
		}

		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},

	refresh: function(frm) {
		if(frm.doc.docstatus == 0 && frm.doc.set_posting_time) {
			frm.set_df_property('posting_date', 'read_only', 0);
			frm.set_df_property('posting_time', 'read_only', 0);
		} else {
			frm.set_df_property('posting_date', 'read_only', 1);
			frm.set_df_property('posting_time', 'read_only', 1);
		}
		if(frm.doc.docstatus > 0 ) {
            if(frm.doc.voucher_no != null){
                frm.add_custom_button(__('Accounting Ledger'), function() {
                    frappe.route_options = {
                        voucher_no: frm.doc.voucher_no,
                        from_date: frm.doc.enrollment_date,
                        to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
                        company: frm.doc.company,
                        group_by: '',
                        show_cancelled_entries: frm.doc.docstatus === 2
                    };
                    frappe.set_route("query-report", "General Ledger");
                }, __("View"));
            }
			
		}


	},

	
    	
});

