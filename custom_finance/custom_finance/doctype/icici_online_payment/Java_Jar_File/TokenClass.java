cdimport com.fiserv.fdc.FDConnectUtils;
import com.fiserv.fdc.sale.model.FDConnectSaleRequest;
import com.fiserv.fdc.sale.model.FDConnectSaleResponse;
import com.fiserv.fdc.response.model.FDConnectDecryptRequest;
import com.fiserv.fdc.response.model.FDConnectDecryptResponse;
import com.fiserv.fdc.inquiry.model.FDConnectInquiryRequest;
import com.fiserv.fdc.inquiry.model.FDConnectInquiryResponse;
import com.google.gson.Gson;
import java.awt.Desktop;
import java.io.IOException;
import java.net.URI;

public class TokenClass {

    public static String getToken(String merchantId, String key, String iv, String apiURL, String amount, String currencyCode, String merchantTxnId, String transactionType, String resultURL) throws IOException {
        
        FDConnectSaleRequest request = new FDConnectSaleRequest(merchantId,key,iv,apiURL,amount,currencyCode,merchantTxnId,transactionType,resultURL);
        FDConnectSaleResponse resp = FDConnectUtils.saleTxn(request);
        String tokenId=resp.getSessionTokenId();
        return tokenId;
    }
   
    public static String getDecryptResponse(String merchantId,String encData,String fdcTxnId,String apiURL) throws IOException {
        
        FDConnectDecryptRequest fdConnectDecryptRequest = new FDConnectDecryptRequest(merchantId,encData,fdcTxnId,apiURL);
        FDConnectDecryptResponse resp = FDConnectUtils.decryptMsg(fdConnectDecryptRequest);
        String decData=new Gson().toJson(resp);
        return decData;
    }

    public static String inquiryTest(String merchantId,String key,String iv,String apiURL,String merchantTxnId,String fpTransactionId) throws IOException {
    
        FDConnectInquiryRequest firstPayInquiryRequest =new FDConnectInquiryRequest(merchantId,key,iv,apiURL,merchantTxnId,fpTransactionId); 
        FDConnectInquiryResponse resp = FDConnectUtils.inquiryTxn(firstPayInquiryRequest);

        String inquiryStatus= new Gson().toJson(resp);
        return inquiryStatus;
    }

     public static String getTokenNew(String merchantId, String key, String iv, String apiURL, String amount, String currencyCode, String merchantTxnId, String transactionType, String resultURL,String Udf) throws IOException {
        
        
        FDConnectSaleRequest request = new FDConnectSaleRequest();
        request.setMerchantId(merchantId);
        request.setKey(key);
        request.setIv(iv);
        request.setApiURL(apiURL);
        request.setAmount(amount);
        request.setCurrencyCode(currencyCode);
        request.setMerchantTxnId(merchantTxnId);
        request.setTransactionType(transactionType);
        request.setUdf5(Udf);
        request.setResultURL(resultURL);

        FDConnectSaleResponse resp = FDConnectUtils.saleTxn(request);                     
        String tokenId=resp.getSessionTokenId();
        return tokenId;
    }
}


   