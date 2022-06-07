frappe.ui.form.on("Exam Declaration Fee Item", "fee_structure", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var a=0;
    if (d.fee_structure){
        a=frm.doc.fee_structure.length;
        frm.set_value("fee_structure_count", a);
        if(a>=1){
            frm.set_df_property('fee_structure', 'cannot_add_rows', true);
            frm.set_df_property('fee_structure', 'cannot_delete_rows', true);
        }
    }
});