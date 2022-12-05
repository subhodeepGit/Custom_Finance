# Copyright (c) 2022, SOUL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from jpype import startJVM, shutdownJVM, java, addClassPath, JClass, JInt
addClassPath("/opt/bench/frappe-bench/apps/icici_integration/icici_integration/icici_integration/doctype/onlinepayment/TokenClass.jar")
addClassPath("/opt/bench/frappe-bench/apps/icici_integration/icici_integration/icici_integration/doctype/onlinepayment/CommerceConnect.jar")
from urllib.request import urlopen
from custom_finance.custom_finance.notification.custom_notification import online_payment_submit
import json


class ICICIOnlinePayment(Document):
	
	def on_cancel(doc):
		frappe.throw("Once form is submitted it can't be cancelled")
	def on_submit(doc): 
		getTransactionDetails(doc,doc.name)  
		frappe.msgprint("Your Transaction is completed. Your Transaction Id is " + doc.transaction_id)
		online_payment_submit(doc)


		# def __init__(self):		
		# 	self.getTransactionDetails(doc,doc.name)  
		# 	# frappe.msgprint("Your Transaction is completed. Your Transaction Id is " + doc.transaction_id)
			

@frappe.whitelist()
def get_outstanding_amount(student):
	fee_voucher_list=frappe.get_all("Fees",filters=[["student","=",student],["outstanding_amount","!=",0],["docstatus","=",1]],
															fields=['outstanding_amount'],
															order_by="due_date asc")
	outstanding_amount=0
	for t in fee_voucher_list:
		outstanding_amount=t['outstanding_amount']+outstanding_amount
		print("outstanding_amount",outstanding_amount)
	return outstanding_amount



def getTransactionDetails(doc,name):   
	# getDoc=frappe.get_doc("ICICI Settings")
	getDoc=frappe.get_doc("ICICI settings Production")
	merchantId = getDoc.merchantid
	key=getDoc.key
	iv=getDoc.iv
	merchantTxnId=name
	fpTransactionId=""
	# apiURL="https://test.fdconnect.com/FirstPayL2Services/getTxnInquiryDetail"    #Test Api
	apiURL="https://www.fdconnect.com/FDConnectL3Services/getTxnInquiryDetail"       #Production Api
	try: 
		tokenclass = JClass('TokenClass')
		transactionDetailsData = tokenclass.inquiryTest(java.lang.String("%s"% merchantId), java.lang.String("%s"% key),
											java.lang.String("%s"%iv),java.lang.String("%s"% apiURL),
											java.lang.String("%s"% merchantTxnId),
											java.lang.String("%s"% fpTransactionId)) 
		
		transactionDetailsData = json.loads(str(transactionDetailsData)) 
		# print("transactionDetailsData-->",transactionDetailsData)  
		   
		frappe.db.set_value("OnlinePayment",transactionDetailsData["saleTxnDetail"]["merchantTxnId"],"transactionid",transactionDetailsData["fpTransactionId"])
		frappe.db.set_value("OnlinePayment",transactionDetailsData["saleTxnDetail"]["merchantTxnId"],"transaction_status",transactionDetailsData["saleTxnDetail"]["transactionStatus"])        
		frappe.db.set_value("OnlinePayment",transactionDetailsData["saleTxnDetail"]["merchantTxnId"],"transaction_status_description",transactionDetailsData["saleTxnDetail"]["transactionStatusDescription"])         
		frappe.db.commit() 

		doc.transaction_id=transactionDetailsData["fpTransactionId"] 
		doc.transaction_status=transactionDetailsData["saleTxnDetail"]["transactionStatus"]
		doc.transaction_status_description=transactionDetailsData["saleTxnDetail"]["transactionStatusDescription"]
			   
	except Exception as err:
		print(repr(err))

	return str(transactionDetailsData) 





# @frappe.whitelist()        
# def getSessionToken(name,paying_amount):  
    
# 	getDoc=frappe.get_doc("ICICI Settings")
# 	merchantId = getDoc.merchantid
# 	key=getDoc.key      
# 	iv=getDoc.iv
# 	configId= getDoc.configid
# 	apiURL="https://test.fdconnect.com/FirstPayL2Services/getToken"     
# 	amountValue=paying_amount  	      
# 	currencyCode="INR" 
# 	merchantTxnId=name  
# 	transactionType="sale"    
	 

# 	# resultURL="http://10.0.160.184:8000/paymentreturn?id=" + name   #local     
   
# 	resultURL="https://paymentkp.eduleadonline.com/paymentreturn?id=" + name  #server

# 	try:
# 		tokenclass = JClass('TokenClass') 
# 		tokenId = tokenclass.getToken(java.lang.String("%s"% merchantId), java.lang.String("%s"% key),
# 							java.lang.String("%s"%iv),java.lang.String("%s"% apiURL),
# 							java.lang.String("%s"% amountValue),java.lang.String("%s"% currencyCode),java.lang.String("%s"% merchantTxnId),
# 							java.lang.String("%s"% transactionType),java.lang.String("%s"% resultURL))
		
# 		if str(tokenId) != None:
# 			newURL= "https://test.fdconnect.com/Pay/?sessionToken=" + str(tokenId) + "&configId="+configId;             
		   
# 		else :
# 			frappe.throw("Session has expired. Please create new transaction")  
					
# 	except Exception as err:
# 		print(repr(err))

# 	return {"TokenId":str(tokenId),"configId":configId}


# @frappe.whitelist()
# def getDecryptedData(doc,encData=None,fdcTxnId=None):  
# 	getDoc=frappe.get_doc("ICICI Settings")
# 	merchantId = getDoc.merchantid
# 	apiURL="https://test.fdconnect.com/FirstPayL2Services/decryptMerchantResponse" 
# 	try:
		
# 		if encData!=None and fdcTxnId!=None:
# 			tokenclass = JClass('TokenClass')
# 			decData = tokenclass.getDecryptResponse(java.lang.String("%s"% merchantId), java.lang.String("%s"% encData),
# 													java.lang.String("%s"%fdcTxnId),java.lang.String("%s"% apiURL))             
# 			decData = json.loads(str(decData))
		
			
			
# 			# if decData["merchantTxnId"]!= None:
# 			# 	id= frappe.get_doc("OnlinePayment",decData["merchantTxnId"])

# 			if (decData["transactionStatus"]=="FAILED"):
# 				ct = datetime.datetime.now() 
				               
# 			else:
# 				ct=decData["transactionDateTime"]
# 	except Exception as e: 
# 		print(repr(e))

# 	if decData==None:
# 		pass
# 	# elif decData["errorCode"] != None:
# 	# 	pass			
# 	else:
# 		return {"transactionid":decData["fpTransactionId"],"transaction_status":decData["transactionStatus"],
# 						"transaction_status_description":decData["transactionStatusDescription"],"datetime":ct}


# @frappe.whitelist()
# def submission(doc): 
#     if doc:
#         submitDoc= frappe.get_doc("OnlinePayment",doc)
#         submitDoc.submit()

