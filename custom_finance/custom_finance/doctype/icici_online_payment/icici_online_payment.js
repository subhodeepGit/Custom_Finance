// Copyright (c) 2022, SOUL and contributors
// For license information, please see license.txt

frappe.ui.form.on('ICICI Online Payment', {
	party: function(frm) {
		frappe.call({
			method:"custom_finance.custom_finance.doctype.icici_online_payment.icici_online_payment.get_outstanding_amount",
			args: {
				student: frm.doc.party
			},
			callback: function(r){
				// if(r.message){
					var result = r.message;
					frm.set_value("total_outstanding_amout",result);
					frm.set_value("paying_amount",result);
				// }
			}
		})
	}
});
frappe.ui.form.on("ICICI Online Payment", "refresh", function(frm){
	frm.add_custom_button("Online Payment", function(){
		
 
	 frappe.call({		  
		method: "custom_finance.custom_finance.doctype.icici_online_payment.icici_online_payment.getSessionToken",	
		args: {	
			 
			name:frm.doc.name,
			paying_amount:frm.doc.paying_amount,
 
	   },
		   
		 callback: function(r) {
			 var sessionId=r.message["TokenId"]
			 var configId=r.message["configId"]				
			 window.open("https://test.fdconnect.com/Pay/?sessionToken=" + sessionId + "&configId="+ configId,"_self")
			  
		   }
	   });
 
	 });

	 
 }); 
 
 frappe.ui.form.on('ICICI Online Payment', {
	refresh(frm) { 
		
		if (frm.is_new() && frm.doc.docstatus === 0){
			frm.remove_custom_button('Online Payment');	
		}
		
		if (!frm.is_new() && frm.doc.docstatus === 0){	
			$('.primary-action').prop('disabled', true);
		}
		
		if (!frm.is_new() && frm.doc.docstatus === 1){	            
			frm.remove_custom_button('Online Payment');
		}
	}
});
 frappe.ui.form.on("ICICI Online Payment", "refresh", function(frm) {	
	
	 var  queryString = window.location.search;
	 var urlParams = new URLSearchParams(queryString);
	 var fpTxnId = urlParams.get('fpTxnId');
	 var encData = urlParams.get('encData');

	 frappe.call({		  
		method: "custom_finance.custom_finance.doctype.icici_online_payment.icici_online_payment.getDecryptedData",	
		args: {
			doc:frm.doc,
			encData:encData,
			fdcTxnId:fpTxnId

	    },		  
		callback: function(r) {
			var transaction_id=r.message["transactionid"]				
			var transaction_status=r.message["transaction_status"]				
			var transaction_status_description=r.message["transaction_status_description"]	
			var date_time_of_transaction=r.message["datetime"]	

			frm.doc.transaction_id = transaction_id
			frm.doc.transaction_status=transaction_status
			frm.doc.transaction_status_description=transaction_status_description
			frm.doc.date_time_of_transaction=date_time_of_transaction

			frm.refresh_field("transaction_id");
			frm.refresh_field("transaction_status");
			frm.refresh_field("transaction_status_description");
			frm.refresh_field("date_time_of_transaction");
			if (!frm.is_new() && frm.doc.docstatus === 0 && frm.doc.transaction_id != undefined  ){
				$('.primary-action').prop('disabled', false);
			if (!frm.is_new() && frm.doc.docstatus === 0 && frm.doc.transaction_status != undefined){
					frm.remove_custom_button('Online Payment');	
				}	

			}
			// frappe.call({		  
			// 	method: "custom_finance.custom_finance.doctype.icici_online_payment.icici_online_payment.submission",		        
			// 	args: {
			// 		doc:frm.doc.name,
			// 	},			
	
			// })
			
		   
	    }

	  
 	});

	
 }); 
 frappe.ui.form.on('ICICI Online Payment', {
    refresh(frm) {  
		if (frm.is_new()){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'green',
                message: __(' <b>Important Points <b> :- <br><b>01. KIIT 0% Processing Fee ICICI payment Gateway. <br>  <b>02. <b>   Students of the KIIT University can make all kinds of payment such as admission fees, examination fees, tuition fees, hostel fees, library fees etc. to the University through the online payment facility. It is available 24x7.<br>  <b>03. <b>   If the payment process is not completed, but the respective amount is debited from the Bank-account of the student, the corresponding amount would be credited back .<br>  <b>04. <b>   Every effort has been made by the University to ensure that the online payment system is accurately and correctly operated through the given system. <br> If due to failure in link, or any error either in the process or in the server of the bank, the online payment fails, the University would not be responsible for the non-payment, in which event the student should prefer to make the payment manually.'
                )
            });
        }    
	}
});

frappe.ui.form.on("ICICI Online Payment", "refresh", function(frm) {
    frm.set_df_property("paying_amount", "read_only", frm.is_new() ? 0 : 1);
});
