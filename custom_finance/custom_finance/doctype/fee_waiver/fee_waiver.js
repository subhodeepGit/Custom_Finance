// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fee Waiver', {
	onload: function(frm) {
		frm.set_query("academic_term", function() {
			return{
				"filters": {
					"academic_year": (frm.doc.academic_year)
				}
			};
		});
		if (!frm.doc.posting_date) {
			frm.doc.posting_date = frappe.datetime.get_today();
		}
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 && frm.doc.set_posting_time) {
			frm.set_df_property('posting_date', 'read_only', 0);
			frm.set_df_property('posting_time', 'read_only', 0);
		} else {
			frm.set_df_property('posting_date', 'read_only', 1);
			frm.set_df_property('posting_time', 'read_only', 1);
		}
	},
	student: function(frm) {
		if (frm.doc.student){
            frm.trigger("set_program_enrollment");
            frm.set_query("programs", function() {
                return {
                    query: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_progarms',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("program", function() {
                return {
                    query: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_sem',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("academic_term", function() {
                return {
                    query: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_term',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("academic_year", function() {
                return {
                    query: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_year',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("student_category", function() {
                return {
                    query: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_student_category',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("student_batch", function() {
                return {
                    query: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_batch',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
        }
	},
	set_program_enrollment(frm) {
        frappe.call({
            method: "custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_program_enrollment",
            args: {
                student: frm.doc.student,
            },
            callback: function(r) { 
                if (r.message){
                    frm.set_value("program_enrollment",r.message['name'])
                }
            } 
            
        });    
        
	},
});

frappe.ui.form.on('Fee Waiver', {
	//  open of pop up 
	get_fees_voucher: function(frm) {
		const today = frappe.datetime.get_today();
		const fields = [
			{fieldtype:"Section Break", label: __("Posting Date")},
			{fieldtype:"Date", label: __("From Date"),
				fieldname:"from_posting_date", default:frappe.datetime.add_days(today, -30)},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_posting_date", default:today},
			{fieldtype:"Section Break", label: __("Due Date")},
			{fieldtype:"Date", label: __("From Date"), fieldname:"from_due_date"},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_due_date"},
			{fieldtype:"Section Break", label: __("Outstanding Amount")},
			{fieldtype:"Float", label: __("Greater Than Amount"),
				fieldname:"outstanding_amt_greater_than", default: 0},
			{fieldtype:"Column Break"},
			{fieldtype:"Float", label: __("Less Than Amount"), fieldname:"outstanding_amt_less_than"},
			{fieldtype:"Section Break"},
			{fieldtype:"Link", label:__("Cost Center"), fieldname:"cost_center", options:"Cost Center",
				"get_query": function() {
					return {
						"filters": {"company": frm.doc.company}
					}
				}
			},
			{fieldtype:"Column Break"},
			{fieldtype:"Section Break"},
			{fieldtype:"Check", label: __("Allocate Payment Amount"), fieldname:"allocate_payment_amount", default:1},
		];

		frappe.prompt(fields, function(filters){
			frappe.flags.allocate_payment_amount = true;
			frm.events.validate_filters_data(frm, filters);
			frm.doc.cost_center = filters.cost_center;
			frm.events.get_outstanding_documents(frm, filters);
		}, __("Filters"), __("Get Outstanding Documents"));
	},

	validate_filters_data: function(frm, filters) {
		const fields = {
			'Posting Date': ['from_posting_date', 'to_posting_date'],
			'Due Date': ['from_posting_date', 'to_posting_date'],
			'Advance Amount': ['from_posting_date', 'to_posting_date'],
		};

		for (let key in fields) {
			let from_field = fields[key][0];
			let to_field = fields[key][1];

			if (filters[from_field] && !filters[to_field]) {
				frappe.throw(
					__("Error: {0} is mandatory field", [to_field.replace(/_/g, " ")])
				);
			} else if (filters[from_field] && filters[from_field] > filters[to_field]) {
				frappe.throw(
					__("{0}: {1} must be less than {2}", [key, from_field.replace(/_/g, " "), to_field.replace(/_/g, " ")])
				);
			}
		}
	},

	get_outstanding_documents: function(frm, filters) {
		frm.clear_table("fee_componemts");
		if(!frm.doc.student) {
			return;
		}

		// frm.events.check_mandatory_to_fetch(frm);
		var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;
		alert("ok")
		var args = {
			"posting_date": frm.doc.posting_date,
			"company": frm.doc.company,
			// "party_type": frm.doc.party_type,
			// "payment_type": frm.doc.payment_type,
			"party": frm.doc.student,
			// "party_account": frm.doc.payment_type=="Receive" ? frm.doc.paid_from : frm.doc.paid_to,
			"cost_center": frm.doc.cost_center
		}

		for (let key in filters) {
			args[key] = filters[key];
		}

		frappe.flags.allocate_payment_amount = filters['allocate_payment_amount'];

		return  frappe.call({
			method: 'custom_finance.custom_finance.doctype.fee_waiver.fee_waiver.get_outstanding_fees',
			args: {
				args:args
			},
			callback: function(r, rt) {
				if(r.message) {
					(r.message).forEach(element => {
                        var c = frm.add_child("fee_componemts")
                        c.fees_category = element.fees_category
						// c.reference_doctype=element.Type
						// c.reference_name=element.reference_name
						// c.due_date=element.posting_date
						// c.allocated_amount=element.outstanding_fees
						// c.total_amount=element.outstanding_fees
						// c.outstanding_amount=element.outstanding_fees
						// c.account_paid_from=element.receivable_account
                    });
                    frm.refresh_field("fee_componemts")
				}
			}
		});
	},


});