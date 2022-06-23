// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Review Request', {
	onload: function(frm) {
		frm.set_query("doc_type_names", function() {
			return{
				filters:{
				"name": ["in", ["Fees","Payment Entry","Payment Refund"]],
			}
		}
		});
	}
});
// frappe.ui.form.on("Room Allotment", "doc_type_names", function(frm) {

// 	set_field_options("doc_type_names", ["Fees","Payment Entry"])

//   });
