import time, hmac, hashlib

class SignatureInformation:
    request_timestamp:int = 0
    signatures = []

    def __init__(self, request_header:str):
        signature_headers = request_header.split(",")
        for signature in signature_headers:
            header, value = signature.split("=")
            if header == "t":
                self.request_timestamp = int(value)
            elif header == "v1":
                self.signatures.append(value) 
    
    def is_request_time_valid(self, tolerance:int) -> bool:
        current_time = self.get_current_unix_time()
        time_calculation:int = self.request_timestamp + tolerance
        return current_time < (time_calculation)

    def is_signature_safe(self, requestBody:str, signingSecret:str) -> bool:
        hashValue = self.__compute_hash(requestBody, signingSecret)
        return hashValue in self.signatures

    def __compute_hash(self, requestBody:str, signingSecret:str) -> str:
        data = str(self.request_timestamp) + "." + requestBody
        return hmac.new(bytes(signingSecret, 'utf-8'), data.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

    def get_current_unix_time(self) -> int:
        return int(time.time())
