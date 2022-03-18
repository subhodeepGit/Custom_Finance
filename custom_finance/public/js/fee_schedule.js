frappe.ui.form.on('Fee Schedule',{
    setup: function(frm) {
        frm.set_query("academic_term", function() {
            return {
                filters: {
                    "academic_year":frm.doc.academic_year
                }
            };
        });
        frm.set_query("program", function() {
            return {
                filters: {
                    "programs":frm.doc.programs
                }
            };
        });
    },
    refresh:function(frm){
        frm.set_query("student_group","student_groups", function() {
            return {
                filters: {
                    "program":frm.doc.program
                }
            };
        });
    }
})