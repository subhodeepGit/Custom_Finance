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