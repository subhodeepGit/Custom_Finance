frappe.ui.form.on('Fee Structure', {
	program(frm) {
        frm.clear_table("course_wise_fees");
        if (frm.doc.program){
                frappe.call({
                    method: "kp_edtec.kp_edtec.doctype.fee_structure.get_courses",
                    args: {
                        program: frm.doc.program,
                    },
                    callback: function(r) { 
                        (r.message).forEach(element => {
                            var c = frm.add_child("course_wise_fees")
                            c.course=element.course
                        });
                        frm.refresh_field("course_wise_fees")
                    } 
                    
                });    
        }
	},
    setup(frm){
        frm.set_query("program",function(){
            return{
                filters:{
                    "programs":frm.doc.programs
                }
            }
        })
    },
  //   refresh(frm){
  //       frappe.call({
		// 	method: "kp_edtec.kp_edtec.doctype.fee_structure.get_fee_types",
		// 	callback: function(r) {
		// 		frm.set_df_property("fee_type", "options", r.message);
		// 	}
		// });
  //   }
})


frappe.ui.form.on("Fee Component", "fees_category", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (d.fees_category){
        var total_amount=0;
        (cur_frm.doc.course_wise_fees).forEach(e=>{
            total_amount+=(e.amount ? e.amount:0)
        })
        d.amount=total_amount;
        refresh_field("amount", d.name, d.parentfield);
    }
});

// Custom finance
// Calculate grand Total	
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

// filter income account receivable account
frappe.ui.form.on('Fee Structure', {
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
					'is_group': d.is_group = 0
				}
			};
		});
		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	}
	

});
frappe.ui.form.on('Fee Structure', {
    onload:function(frm) {
		if(frappe.user.has_role(["Accounts User","Student","Education Administrator"]) && !frappe.user.has_role(["Administrator"])){
  			frm.remove_custom_button('Create Fee Schedule');
        }
	}
}


);
