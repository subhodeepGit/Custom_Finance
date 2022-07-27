// frappe.ui.form.on('Payment Entry', {
// 	// allocated_amount:function(frm, cdt, cdn){
// 	// 	var d = locals[cdt][cdn];
// 	// 	var total = 0;
//     //     alert("ok")
// 	// 	let a= parseInt(total)
// 	// 	frm.doc.references.forEach(function(d)  { a = a+ d.allocated_amount; });
// 	// 	frm.set_value("paid_amount", a);
// 	// 	refresh_field("paid_amount");
// 	// },
// 	// references_remove:function(frm, cdt, cdn){
// 	// 	var d = locals[cdt][cdn];
// 	// 	var total = 0;
// 	// 	let a= parseInt(total)
// 	// 	frm.doc.references.forEach(function(d) { a += d.allocated_amount; });
// 	// 	frm.set_value("paid_amount", a);
// 	// 	refresh_field("paid_amount");
// 	// }
//     refresh: function(frm) {
//         frm.set_value("paid_amount", total_allocated_amount);
//     }

// });

//For Razorpay
frappe.ui.form.on("Payment Entry", "refresh", function(frm){
    if(frm.doc.mode_of_payment == "Online Payment" && cur_frm.doc.__unsaved!=1 && frm.doc.status!="Submitted" && frm.doc.razorpay_id==undefined){
	frm.add_custom_button("Online Payment", function(){
			// window.location.href = "";
			frappe.call({
				method: "custom_finance.custom_finance.validations.online_fees.make_payment",								
				args: {
                        full_name:frm.doc.party_name,
                        email_id:frm.doc.student_email,
                        amount:frm.doc.paid_amount,
                        doctype:"Payment Entry",
                        name:frm.doc.name						
				},
				callback: function(r) {
					var res=r.message;
                    localStorage.clear();
                    sessionStorage.clear();
                    window.location.href = r.message;
				}
			});
	});
    }
	else if( frappe.user.has_role(["Education Administrator"]) && !frappe.user.has_role(["Administrator"])){
		frm.remove_custom_button("Online Payment");
	}
	else{
	}
});

frappe.ui.form.on('Payment Entry', {
	//  open of pop up 
	get_outstanding_fees: function(frm) {
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
		frm.clear_table("references");

		if(!frm.doc.party) {
			return;
		}

		frm.events.check_mandatory_to_fetch(frm);
		var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;

		var args = {
			"posting_date": frm.doc.posting_date,
			"company": frm.doc.company,
			"party_type": frm.doc.party_type,
			"payment_type": frm.doc.payment_type,
			"party": frm.doc.party,
			"party_account": frm.doc.payment_type=="Receive" ? frm.doc.paid_from : frm.doc.paid_to,
			"cost_center": frm.doc.cost_center
		}

		for (let key in filters) {
			args[key] = filters[key];
		}

		frappe.flags.allocate_payment_amount = filters['allocate_payment_amount'];

		return  frappe.call({
			method: 'custom_finance.custom_finance.doctype.payment_entry.get_outstanding_fees',
			args: {
				args:args
			},
			callback: function(r, rt) {
				if(r.message) {
					// alert(r.message)
					var total_positive_outstanding = 0;
					var total_negative_outstanding = 0;

					// $.each(r.message, function(i, d) {
					// 	alert(JSON.stringify(d))
					// 	var c = frm.add_child("references");
					// 	c.fees_category=d.fees_category;
					(r.message).forEach(element => {
                        var c = frm.add_child("references")
                        c.fees_category = element.fees_category
						c.program=element.program
						c.reference_doctype=element.Type
						c.reference_name=element.reference_name
						c.due_date=element.posting_date
						c.allocated_amount=element.outstanding_fees
						c.total_amount=element.outstanding_fees
						c.outstanding_amount=element.outstanding_fees
						c.account_paid_from=element.receivable_account
                    });
                    frm.refresh_field("references")
				}

			}
		});
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
}

});
frappe.ui.form.on('Payment Entry', {
	student(frm){
		if (frm.doc.student) {
			frappe.call({
				// /opt/bench/frappe-bench/apps/custom_finance/custom_finance/custom_finance/doctype/payment_entry.py
				method: 'custom_finance.custom_finance.doctype.payment_entry.get_student_detai',
				args: {
					args:args
				},
				callback: function(r) {
					if (r.message) {
						(r.message).forEach(function (element) {
								var c = frm.add_child("references");
								c.semesters = element.program;
							});
					}
					frm.refresh();
					refresh_field('references');
				}
			});
		}
	}
});
frappe.ui.form.on("Payment Entry","mode_of_payment", function(frm){
	
    var mop = frm.doc.mode_of_payment
    if(mop == "Online Payment"){
        frm.doc.reference_no = "Online Payment"
        frm.set_value("reference_no",frm.doc.reference_no)
        frm.set_value("reference_date", frappe.datetime.nowdate());
        frm.refresh();
    };
});

frappe.ui.form.on("Payment Entry","reference_no", function(frm){
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

frappe.ui.form.on('Payment Entry', {
	onload: function(frm) {
		frm.set_query("account_paid_from","references", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'name': "Fees Refundable / Adjustable - KP",
					'company': frm.doc.company,
					// 'account_type': d.account_type = 'Income Account',
					'is_group': d.is_group = 0,
				}
			};
		});
		frm.set_query("account_paid_to","references", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					// 'name': "Fees Refundable / Adjustable - KP",
					'company': frm.doc.company,
					// 'account_type': d.account_type = 'Income Account',
					'is_group': d.is_group = 0,
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
		frm.set_query("reference_name", "references", function(doc, cdt, cdn) {
			const child = locals[cdt][cdn];
			let ost = doc.outstanding_amount;
			alert(doc.company)
			const filters = {"outstanding_amount": ost > 0, "docstatus": 1, "company": doc.company};
			const party_type_doctypes = ['Sales Invoice', 'Sales Order', 'Purchase Invoice',
				'Purchase Order', 'Expense Claim', 'Fees', 'Dunning', 'Donation'];

			if (in_list(party_type_doctypes, child.reference_doctype)) {
				filters[doc.party_type.toLowerCase()] = doc.party;
			}

			if(child.reference_doctype == "Expense Claim") {
				filters["docstatus"] = 1;
				filters["is_paid"] = 0;
			}
		});

		frm.set_query("reference_name", "references", function (doc, cdt, cdn) {
			return {
				filters: [
					["Fees", "student", "=", doc.party],
					["Fees", "outstanding_amount", ">", 0],
					["Fees", "docstatus", "=", 1],
					["Fees", "company", "=", doc.company]
				]
			}
		});
		// Rupali:Code for Refund amount:Start	
		
		if (frm.doc.paid_amount == undefined){
			frm.set_df_property("paid_amount","read_only",0);	
			var df = frappe.meta.get_docfield("Payment Entry Reference","account_paid_from", frm.doc.name);
			df.read_only = 1
			var df1 = frappe.meta.get_docfield("Payment Entry Reference","account_paid_to", frm.doc.name);
			df1.read_only = 0		
			
			
		} else  
		   frm.set_df_property("paid_amount","read_only",1);
        // Rupali:Code for Refund amount:End	
		
		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},
})

frappe.ui.form.on('Payment Entry Reference',"reference_name",function(frm, cdt, cdn){
	var d=locals[cdt][cdn];
	if(d.fees_category=="Fees Refundable / Adjustable" && d.account_paid_from=="Fees Refundable / Adjustable - KP"){
		d.total_amount=0
		d.outstanding_amount=0
		d.allocated_amount=0
	}
})


// frappe.ui.form.on("Payment Entry Reference", "allocated_amount", function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//         frappe.db.get_value("Payment Entry Reference", {"allocated_amount": d.allocated_amount}, "total_amount", function(value) {
//             d.total_amount = value.total_amount;
//         });
// });

frappe.ui.form.on('Payment Entry Reference',"allocated_amount",function(frm, cdt, cdn){
	var d=locals[cdt][cdn];
	if(d.fees_category=="Fees Refundable / Adjustable" && d.account_paid_from=="Fees Refundable / Adjustable - KP"){
		d.total_amount=d.allocated_amount
		d.outstanding_amount=d.allocated_amount
	}
})

frappe.ui.form.on("Payment Entry","mode_of_payment", function(frm){
	
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



