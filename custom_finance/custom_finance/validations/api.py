import frappe


@frappe.whitelist()
def get_fee_components(fee_structure):
    """Returns Fee Components.

    :param fee_structure: Fee Structure.
    """
    if fee_structure:
        fs = frappe.get_all("Fee Component", fields=["fees_category", "receivable_account", "income_account", "grand_fee_amount", "outstanding_fees", "description", "amount"] , filters={"parent": fee_structure}, order_by= "idx")
        return fs