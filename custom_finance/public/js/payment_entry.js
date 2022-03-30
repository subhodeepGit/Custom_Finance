frappe.ui.form.on('Payment Entry', {
	// allocated_amount:function(frm, cdt, cdn){
	// 	var d = locals[cdt][cdn];
	// 	var total = 0;
    //     alert("ok")
	// 	let a= parseInt(total)
	// 	frm.doc.references.forEach(function(d)  { a = a+ d.allocated_amount; });
	// 	frm.set_value("paid_amount", a);
	// 	refresh_field("paid_amount");
	// },
	// references_remove:function(frm, cdt, cdn){
	// 	var d = locals[cdt][cdn];
	// 	var total = 0;
	// 	let a= parseInt(total)
	// 	frm.doc.references.forEach(function(d) { a += d.allocated_amount; });
	// 	frm.set_value("paid_amount", a);
	// 	refresh_field("paid_amount");
	// }
    refresh: function(frm) {
        frm.set_value("paid_amount", total_allocated_amount);
    }

});