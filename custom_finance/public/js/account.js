frappe.ui.form.on('Account', {
    add_toolbar_buttons: function(frm) {
		if(frappe.user.has_role(["Accounts User",,"Accounts Manager","Student"]) && !frappe.user.has_role(["Education Administrator"])){
  			frm.remove_custom_button('Convert to Group','Actions');
              frm.remove_custom_button('Chart of Accounts','View');
        }
	}
}
);