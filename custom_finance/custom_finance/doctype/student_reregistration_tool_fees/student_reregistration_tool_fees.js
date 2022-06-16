// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Reregistration Tool Fees', {
	setup: function(frm) {
		frm.add_fetch("student", "title", "student_name");
		frm.add_fetch("student_applicant", "title", "student_name");
		if(frm.doc.__onload && frm.doc.__onload.academic_term_reqd) {
			frm.toggle_reqd("academic_term", true);
		}
		frm.set_query("programs", function() {
			return {
				filters: {
					"program_grade":frm.doc.program_grade
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
		frm.set_query("new_semester", function() {
			return {
				filters: {
					"programs":frm.doc.programs
				}
			};
		});
		frm.set_query("academic_term", function() {
			return {
				filters: {
					"academic_year":frm.doc.academic_year
				}
			};
		});
		frm.set_query("new_academic_term", function() {
			return {
				filters: {
					"academic_year":frm.doc.new_academic_year
				}
			};
		});
		frm.set_query("additional_course_1","students", function(frm, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				query: 'kp_edtec.kp_edtec.doctype.student_reregistration_tool.student_reregistration_tool.get_optional_courses',
				filters: {
					"new_semester":frm.new_semester,
				    "additional_course_2":d.additional_course_2,
				    "additional_course_3":d.additional_course_3
				}
			};
		});
		frm.set_query("additional_course_2","students", function(frm, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				query: 'kp_edtec.kp_edtec.doctype.student_reregistration_tool.student_reregistration_tool.get_optional_courses',
				filters: {
					"new_semester":frm.new_semester,
				    "additional_course_1":d.additional_course_1,
				    "additional_course_3":d.additional_course_3
				}
			};
		});
		frm.set_query("additional_course_3","students", function(frm, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				query: 'kp_edtec.kp_edtec.doctype.student_reregistration_tool.student_reregistration_tool.get_optional_courses',
				filters: {
					"new_semester":frm.new_semester,
				    "additional_course_1":d.additional_course_1,
				    "additional_course_2":d.additional_course_2
				}
			};
		});
	},

	"refresh": function(frm) {
		frm.disable_save();
		frm.fields_dict.enroll_students.$input.addClass('btn btn-primary');
		frappe.realtime.on("student_reregistration_tool_fees", function(data) {
			frappe.hide_msgprint(true);
			frappe.show_progress(__("Enrolling students"), data.progress[0], data.progress[1]);
			if (data.reload && data.reload === 1) {
				frm.reload_doc();
			}
		});	

		// frappe.realtime.on('student_reregistration_tool_fees', function(data) {
		// 	if (data.reload && data.reload === 1) {
		// 		frm.reload_doc();
		// 	}
		// 	if (data.progress) {
		// 		let progress_bar = $(cur_frm.dashboard.progress_area.body).find('.progress-bar');
		// 		if (progress_bar) {
		// 			$(progress_bar).removeClass('progress-bar-danger').addClass('progress-bar-success progress-bar-striped');
		// 			$(progress_bar).css('width', data.progress+'%');
		// 		}
		// 	}
		// });	
	},

	"get_students": function(frm) {
		frm.set_value("students",[]);
		frappe.call({
			method: "get_students",
			doc:frm.doc,
			callback: function(r) {
				if(r.message) {
					frm.set_value("students", r.message);
				}
			}
		});
	},

	"enroll_students": function(frm) {
		if (frm.doc.new_semester && frm.doc.new_academic_year){
			frappe.call({
				method: "enroll_students",
				doc:frm.doc,
				callback: function(r) {
					// frm.set_value("students", []);
					frappe.hide_msgprint(true);
				}
			});
		}

	},
	"new_semester": function(frm) {
		if(frm.doc.new_semester){
			frappe.model.with_doc("Program", frm.doc.new_semester, function() {
				var tabletransfer= frappe.model.get_doc("Program", frm.doc.new_semester)
				if(tabletransfer.courses){
					frm.clear_table("courses");
						$.each(tabletransfer.courses, function(index, row){
							if(row.required){
								var d = frm.add_child("courses");
								d.course = row.course;
								d.course_name = row.course_name ;
								frappe.db.get_value("Course", {"name": row.course}, "course_code", function(value) {
											d.course_code = value.course_code;
											frm.refresh_field("courses");
										});
								frm.refresh_field("courses");
							}
						});
	            }
	        });
		}
	}
});