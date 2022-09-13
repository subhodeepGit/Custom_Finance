frappe.ui.form.on('Fees', {
    // setup(frm){
    //     frm.set_query("fee_structure", function() {
    //         return {
    //             query: 'kp_edtec.kp_edtec.doctype.fees.get_fee_structures',
    //             filters: {
    //                 "exam_application":frm.doc.exam_application
    //             }
    //         };
    //     });
    // },

    /////////////// My Code for Filter of table/////
    onload: function(frm) {
		frm.set_query("receivable_account","components", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'company': d.company,
					'account_type': d.account_type = 'Receivable',
					'is_group': d.is_group = 0
				}
			};
		});
		frm.set_query("income_account","components", function(_doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'company': d.company,
					'account_type': d.account_type = 'Income Account',
					'is_group': d.is_group = 0,
                    "liability":0,
				}
			};
		});
		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},
    fee_structure: function(frm) {
		frm.set_value("components" ,"");
		if (frm.doc.fee_structure) {
			frappe.call({
				method: "custom_finance.custom_finance.validations.fees.get_fee_components",
				args: {
					"fee_structure": frm.doc.fee_structure
				},
				callback: function(r) {
					if (r.message) {
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(frm.doc, "Fee Component", "components");
							row.fees_category = d.fees_category;
							row.receivable_account=d.receivable_account;
							row.income_account = d.income_account;
							row.description = d.description;
							row.amount = d.amount;
                            row.grand_fee_amount=d.grand_fee_amount;
                            row.outstanding_fees=d.outstanding_fees;
                            
                            row.waiver_type=d.waiver_type;
                            row.percentage=d.percentage;
                            row.waiver_amount=d.waiver_amount;
                            row.total_waiver_amount=d.total_waiver_amount;
                            
						});
					}
					refresh_field("components");
					frm.trigger("calculate_total_amount");
				}
			});
		}
	},

	//////////////////////////// end of my Code //////////////////////////
    refresh(frm){
        if( frappe.user.has_role(["Student","Education Administrator","Fee Waiver","Transport User"]) && !frappe.user.has_role(["Administrator"])){
            frm.remove_custom_button(__("Return/Refund"));
        }
        else if(frm.doc.docstatus===1 && frm.doc.outstanding_amount==0) {
			frm.add_custom_button(__("Return/Refund"), function() {
                frappe.model.open_mapped_doc({
					method: "ed_tec.ed_tec.doctype.fees.make_refund_fees",
					frm: frm,
				});
			});
		}
        else{
        }
        if(frm.doc.docstatus > 0) {
			frm.add_custom_button(__('General Ledger w/ Cancellation'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: '',
					show_cancelled_entries: frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "Fee General Ledger wth Cancellation");
			}, __("View"));
		}
    },
    // amount(frm){
    //         if(frm.doc.amount){
    //             // frm.doc.outstanding_amount = frm.doc.grand_total - frm.doc.amount;
    //             // frm.doc.waiver_amount = frm.doc.amount
    //             frm.set_value("outstanding_amount",frm.doc.grand_total - frm.doc.amount);
    //             frm.set_value("waiver_amount",frm.doc.amount);

    //         }
    //  },

    // percentage(frm){
    //     if(frm.doc.percentage){
    //         // outstanding_amount = frm.doc.grand_total - (frm.doc.grand_total*(frm.doc.percentage/100));
    //         // waiver_amount = (frm.doc.grand_total*(frm.doc.percentage/100))
    //         frm.set_value("outstanding_amount",frm.doc.grand_total - (frm.doc.grand_total*(frm.doc.percentage/100)));
    //         frm.set_value("waiver_amount",(frm.doc.grand_total*(frm.doc.percentage/100)));
    //     }
    // },
    student(frm){
        if (frm.doc.student){
            frm.trigger("set_program_enrollment");
            frm.set_query("programs", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_progarms',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("program", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_sem',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("academic_term", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_term',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("academic_year", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_year',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("student_category", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_student_category',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("student_batch", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_batch',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            frm.set_query("fee_structure", function() {
                return {
                    query: 'kp_edtec.kp_edtec.doctype.fees.get_fee_structures',
                    filters: {
                        "student":frm.doc.student
                    }
                };
            });
            
        }
    },
	set_program_enrollment(frm) {
        frappe.call({
            method: "custom_finance.custom_finance.validations.fees.get_program_enrollment",
            // method: "kp_edtec.kp_edtec.doctype.program_enrollment.get_program_enrollment",
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
    setup(frm){
        frm.set_query("fees_category","components", function() {
            return {
                // query: 'kp_edtec.kp_edtec.doctype.fees.get_fees_category',
                filters: {
                    "is_refundable_or_adjustable":0,
                }
            };
        });
    }
})
// frappe.ui.form.on("Fee Component", "amount", function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];

//     if(d.amount){
//         d.waiver_on_amount = d.amount 
//         refresh_field("waiver_on_amount", d.name, d.parentfield);
//     }
// })
// frappe.ui.form.on("Fee Component", "waiver_amount", function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//     if(d.waiver_amount && d.amount){
//        d.total_waiver_amount  = d.waiver_amount
//        d.amount =  d.grand_fee_amount -d.waiver_amount
//         refresh_field("amount", d.name, d.parentfield);
//         refresh_field("total_waiver_amount", d.name, d.parentfield);
  
//     }
//     if(!d.amount){
//         frappe.throw("Please add Amount first");
//     }
// });


// frappe.ui.form.on("Fee Component", "percentage", function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//     if(d.percentage && d.amount){
//         d.total_waiver_amount  = ((d.percentage/100) * d.amount)
//         d.amount =  d.amount - ((d.percentage/100) * d.amount)
//         refresh_field("amount", d.name, d.parentfield);
//         refresh_field("total_waiver_amount", d.name, d.parentfield);
  
//     }
//     if(!d.amount){
//         frappe.throw("Please add Amount first");
//     }
// });


// /////////////// My Code for Filter of table/////
// frappe.ui.form.on("Fee Component", "amount", function(frm, cdt, cdn) {
   
//     var ed_details = frm.doc.components;
//     for(var i in ed_details) {
            
//     if (ed_details[i].amount) {
//         // ed_details[i].total_fee_amount="15";
//         ed_details[i].grand_fee_amount=ed_details[i].amount;
//     } 
//    }
//         cur_frm.refresh_field ("components");
    
// });
// frappe.ui.form.on("Fee Component", "amount", function(frm, cdt, cdn) {

//     var ed_details = frm.doc.components;
//     for(var i in ed_details) {
            
//     if (ed_details[i].amount) {
//         // ed_details[i].total_fee_amount="15";
//         ed_details[i].outstanding_fees=ed_details[i].amount;
//     }	 
        
// }
//     cur_frm.refresh_field ("components");

// });
// frappe.ui.form.on("Fee Component", "waiver_amount", function(frm, cdt, cdn) {
//     var cal=locals[cdt][cdn];
//     if (cal.total_waiver_amount) {
//         cal.outstanding_fees=cal.amount;
//     }	 
//     cur_frm.refresh_field ("components");
// });
// frappe.ui.form.on("Fee Component", "percentage", function(frm, cdt, cdn) {
//     var cal=locals[cdt][cdn];
//     if (cal.total_waiver_amount) {
//         cal.outstanding_fees=cal.amount;
//     }	 
//     cur_frm.refresh_field ("components");
// });

frappe.ui.form.on("Fee Component", "amount", function(frm, cdt, cdn) {
   
    var ed_details = frm.doc.components;
    for(var i in ed_details) {
            
    if (ed_details[i].amount) {
        // ed_details[i].total_fee_amount="15";
        ed_details[i].grand_fee_amount=ed_details[i].amount;
    } 
   }
        cur_frm.refresh_field ("components");
    
});
frappe.ui.form.on("Fee Component", "amount", function(frm, cdt, cdn) {

    var ed_details = frm.doc.components;
    for(var i in ed_details) {
            
    if (ed_details[i].amount) {
        // ed_details[i].total_fee_amount="15";
        ed_details[i].outstanding_fees=ed_details[i].amount;
    }	 
        
}
    cur_frm.refresh_field ("components");

});

frappe.ui.form.on("Fee Component", "waiver_amount", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if(d.waiver_amount && d.amount ){
		
        d.amount =  d.grand_fee_amount -d.waiver_amount
        d.total_waiver_amount  = d.waiver_amount
        refresh_field("amount", d.name, d.parentfield);
        refresh_field("total_waiver_amount", d.name, d.parentfield);
		
    }
	else{
		d.amount=d.grand_fee_amount
		d.total_waiver_amount=null
		d.outstanding_fees=d.grand_fee_amount
	}
    if(!d.amount){
        frappe.throw("Please add Amount first");
    }


});

frappe.ui.form.on("Fee Component", "percentage", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
	// var amount=parseInt(d.percentage)
    // if(amount!=0 && percentage<=100){
	// 	d.total_waiver_amount  = ((d.percentage/100) * d.grand_fee_amount)
    //     d.amount =  d.grand_fee_amount - ((d.percentage/100) * d.grand_fee_amount)
	// 	d.total_waiver_amount  = d.grand_fee_amount-d.amount
    //     refresh_field("amount", d.name, d.parentfield);
    //     refresh_field("total_waiver_amount", d.name, d.parentfield);
    // }
	if(d.percentage && d.amount ){
		d.total_waiver_amount  = ((d.percentage/100) * d.grand_fee_amount)
        d.amount =  d.grand_fee_amount - ((d.percentage/100) * d.grand_fee_amount)
		d.total_waiver_amount  = d.grand_fee_amount-d.amount
        refresh_field("amount", d.name, d.parentfield);
        refresh_field("total_waiver_amount", d.name, d.parentfield);
    }
	else{
		d.amount=d.grand_fee_amount
		d.total_waiver_amount=null
		d.outstanding_fees=d.grand_fee_amount
		refresh_field("percentage", d.name, d.parentfield);
	}
    if(!d.amount){
        frappe.throw("Please add Amount first");
    }
});

frappe.ui.form.on("Fee Component", "waiver_type", function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	if(d.waiver_type=="Percentage"||"Amount"){
		d.percentage=null
		d.waiver_amount=null
		d.total_waiver_amount=null
		d.amount=d.grand_fee_amount
        d.outstanding_fees=d.grand_fee_amount
		refresh_field("total_waiver_amount", d.name, d.parentfield);
		refresh_field("percentage", d.name, d.parentfield);
		refresh_field("waiver_amount", d.name, d.parentfield);
		refresh_field("amount", d.name, d.parentfield);
	}
frappe.ui.form.on("Fee Component", "waiver_amount", function(frm, cdt, cdn) {
    var cal=locals[cdt][cdn];
    if (cal.total_waiver_amount) {
        cal.outstanding_fees=cal.amount;
    }	 
    cur_frm.refresh_field ("components");
});
frappe.ui.form.on("Fee Component", "percentage", function(frm, cdt, cdn) {
    var cal=locals[cdt][cdn];
    if (cal.total_waiver_amount) {
        cal.outstanding_fees=cal.amount;
    }	 
    cur_frm.refresh_field ("components");
});
});
frappe.ui.form.on('Fees', {
    onload:function(frm) {
		// if(frm.doc.docstatus===1 && frm.doc.outstanding_amount>0){
  			frm.remove_custom_button('Payment Request','Create');
        }
	}


);
frappe.ui.form.on('Fees', {
    onload:function(frm) {
		if(frappe.user.has_role(["Student","Education Administrator","Fee Waiver","Transport User"]) && !frappe.user.has_role(["Administrator"])){
  			frm.remove_custom_button('Payment','Create');
            frm.remove_custom_button('General Ledger w/ Cancellation','View');
            frm.remove_custom_button('Payments','View');
            frm.remove_custom_button('Accounting Ledger','View');
        }
	}
}


);