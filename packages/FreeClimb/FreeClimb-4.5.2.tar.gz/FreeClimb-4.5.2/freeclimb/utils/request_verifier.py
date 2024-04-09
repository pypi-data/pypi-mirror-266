import sys

from freeclimb.utils.signature_information import SignatureInformation

class RequestVerifier:
    
    DEFAULT_TOLERANCE = 5*60*1000

    @staticmethod
    def verify_request_signature(request_body:str, request_header:str, signing_secret:str, tolerance:int=DEFAULT_TOLERANCE):
        verifier = RequestVerifier()
        verifier.__check_request_body(request_body)
        verifier.__check_request_header(request_header)
        verifier.__check_signing_secret(signing_secret)
        verifier.__check_tolerance(tolerance)
        info = SignatureInformation(request_header)
        verifier.__verify_tolerance(info, tolerance)
        verifier.__verify_signature(info, request_body, signing_secret)
    
    def __check_request_body(self, request_body:str):
        if request_body == "" or request_body == None:
            raise Exception("Request Body cannot be empty or null")

    def __check_request_header(self, request_header:str): 
        if request_header == "" or request_header == None: 
            raise Exception("Error with request header, Request header is empty")
        
        elif not("t" in request_header) :
            raise Exception("Error with request header, timestamp is not present")
        
        elif not("v1" in request_header) :
            raise Exception("Error with request header, signatures are not present")
        

    def __check_signing_secret(self, signing_secret:str):
        if signing_secret == "" or signing_secret == None:
            raise Exception("Signing secret cannot be empty or null")
        
    def __check_tolerance(self, tolerance:int):
        if tolerance <= 0 or tolerance >= sys.maxsize:
            raise Exception("Tolerance value must be a positive integer")
        
    def __verify_tolerance(self, info:SignatureInformation, tolerance:int):
        currentTime = info.get_current_unix_time()
        if not(info.is_request_time_valid(tolerance)):
            raise Exception("Request time exceeded tolerance threshold. Request: " + str(info.request_timestamp)
            + ", CurrentTime: " + str(currentTime) + ", tolerance: " + str(tolerance))

    def __verify_signature(self, info:SignatureInformation, request_body:str, signing_secret:str):
         if not(info.is_signature_safe(request_body, signing_secret)):
            raise Exception("Unverified signature request, If this request was unexpected, it may be from a bad actor. Please proceed with caution. If the request was exepected, please check any typos or issues with the signingSecret")

