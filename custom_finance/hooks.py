from . import __version__ as app_version

app_name = "custom_finance"
app_title = "Custom Finance"
app_publisher = "SOUL"
app_description = "SOUL"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "soul@soulunileaders.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_finance/css/custom_finance.css"
# app_include_js = "/assets/custom_finance/js/custom_finance.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_finance/css/custom_finance.css"
# web_include_js = "/assets/custom_finance/js/custom_finance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "custom_finance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Fees" : "public/js/fees.js",
	"Fee Schedule":"public/js/fee_schedule.js",
	"Fee Structure" : "public/js/fee_structure.js",
	"Payment Entry" : "public/js/payment_entry.js",
	"Program Enrollment":"public/js/program_enrollment.js",
	"Exam Declaration":"public/js/exam_declaration.js",
	"Account":"public/js/account.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_finance.install.before_install"
# after_install = "custom_finance.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_finance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	# "ToDo": "custom_app.overrides.CustomToDo"
	
	"Fees":"custom_finance.custom_finance.doctype.fees.Fees",
	"Payment Entry":"custom_finance.custom_finance.doctype.payment_entry.PaymentEntry",
	"Fee Structure":"custom_finance.custom_finance.doctype.fee_structure.FeeStructure",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Fees":{
        "on_submit":"custom_finance.custom_finance.validations.fees.on_submit",
        "validate":"custom_finance.custom_finance.validations.fees.validate",
        "on_cancel":"custom_finance.custom_finance.validations.fees.on_cancel"
    },
	"Fee Structure":{
		"validate":"custom_finance.custom_finance.validations.fee_structure.validate"
    },
	"Fee Schedule":{
		"validate":"custom_finance.custom_finance.validations.fee_schedule.validate"
    },
	"Payment Entry":{
		"on_submit":["custom_finance.custom_finance.validations.fees_extention.on_submit",
					"custom_finance.custom_finance.validations.online_fees.on_submit"],
		"on_cancel":"custom_finance.custom_finance.validations.fees_extention.on_cancel",
		"validate": "custom_finance.custom_finance.validations.fees_extention.validate",
	},
	"Program Enrollment":{
		"on_submit":"custom_finance.custom_finance.validations.program_enrollment.on_submit",
		"on_cancel":"custom_finance.custom_finance.validations.program_enrollment.on_cancel",
		"validate":"custom_finance.custom_finance.validations.program_enrollment.validate",
	},
	"Exam Declaration":{
		"on_submit":"custom_finance.custom_finance.doctype.exam_declaration.on_submit",
		"on_cancel":"custom_finance.custom_finance.doctype.exam_declaration.on_cancel"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_finance.tasks.all"
# 	],
# 	"daily": [
# 		"custom_finance.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_finance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_finance.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_finance.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "custom_finance.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.doctype.event.event.get_events": "custom_finance.event.get_events"
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry":"custom_finance.custom_finance.doctype.payment_entry.get_payment_entry",	
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details":"custom_finance.custom_finance.doctype.payment_entry.get_party_details",
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details":"custom_finance.custom_finance.doctype.payment_entry.get_account_details",
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_outstanding_reference_documents":"custom_finance.custom_finance.doctype.payment_entry.get_outstanding_reference_documents",
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_company_defaults":"custom_finance.custom_finance.doctype.payment_entry.get_company_defaults",
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_reference_details":"custom_finance.custom_finance.doctype.payment_entry.get_reference_details",
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_party_and_account_balance":"custom_finance.custom_finance.doctype.payment_entry.get_party_and_account_balance",
	"erpnext.education.api.get_fee_components":"custom_finance.custom_finance.validations.api.get_fee_components",
	"erpnext.education.doctype.fee_structure.fee_structure.make_fee_schedule":"custom_finance.custom_finance.doctype.fee_structure.make_fee_schedule",
	"kp_edtec.kp_edtec.doctype.fees.make_refund_fees":"custom_finance.custom_finance.validations.fees.make_refund_fees",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "custom_finance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]


# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"custom_finance.auth.validate"
# ]

# fixtures = [
# 	{"dt": "Custom DocPerm", "filters": [
# 		[
# 			"parent", "not in", [
# 				"DocType"
# 			]
# 		]
# 	]},
	# {"dt": "Translation"},
#     {"dt": "Role"},
#     {"dt": "Role Profile"},
#     {"dt": "Module Profile"},
# ]
after_migrate = [
		'custom_finance.patches.migrate_patch.set_translation',
        'custom_finance.patches.migrate_patch.add_roles',
        'custom_finance.patches.migrate_patch.set_custom_role_permission',
]