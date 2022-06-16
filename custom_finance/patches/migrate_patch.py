import frappe
import os
import json
import sys

#   bench execute custom_finance.patches.migrate_patch.get_custom_role_permission
def get_custom_role_permission(site=None):
    if sys.argv[2]=='--site':
        os.system("bench --site {0} export-fixtures".format(sys.argv[3]))
    else:
        os.system("bench export-fixtures")

#   bench execute custom_finance.patches.migrate_patch.set_custom_role_permission
def set_custom_role_permission():
    with open(frappe.get_app_path("custom_finance","fixtures","custom_docperm.json")) as f:
        for d in json.load(f):
            if len(frappe.get_all('Custom DocPerm',{'parent':d.get('parent'),'role':d.get('role')}))==0:
                role=frappe.new_doc('Custom DocPerm')
                for k in d.keys():
                    role.set(k,d.get(k))
                role.save()



#   bench execute custom_finance.patches.migrate_patch.add_roles
def add_roles():
    with open(frappe.get_app_path("custom_finance","fixtures","role.json")) as f:
        for d in json.load(f):
            if len(frappe.get_all('Role',{'role_name':d.get('role_name')}))==0:
                role=frappe.new_doc('Role')
                for k in d.keys():
                    role.set(k,d.get(k))
                role.save()

#   bench execute custom_finance.patches.migrate_patch.add_roles
def add_module_profile():
    with open(frappe.get_app_path("custom_finance","fixtures","module_profile.json")) as f:
        for d in json.load(f):
            if len(frappe.get_all('Module Profile',{'name':d.get('name')}))==0:
                mp=frappe.new_doc('Module Profile')
                for k in d.keys():
                    mp.set(k,d.get(k))
                mp.save()