import unittest

from freeclimb.utils.signature_information import SignatureInformation

class TestSignatureInformation(unittest.TestCase):
    """SignatureInformation unit test stubs"""

    def setUp(self):
        request_header = "t=1679944186,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"
        self.signature_information = SignatureInformation(request_header)
    
    def tearDown(self):
        pass

    def test_is_request_time_valid_true(self):
        request_header = "t=" + str(self.signature_information.get_current_unix_time()) + ",v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"
        self.signature_information = SignatureInformation(request_header)
        tolerance = 5 * 60 * 1000
        self.assertEqual(self.signature_information.is_request_time_valid(tolerance), True)
    
    def test_is_request_time_valid_false(self):
        request_header = "t=" + str(self.signature_information.get_current_unix_time() - (600 * 60 * 1000)) + ",v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"
        self.signature_information = SignatureInformation(request_header)
        tolerance = 500 * 60 * 1000
        self.assertEqual(self.signature_information.is_request_time_valid(tolerance), False)
    
    def test_is_signature_safe_true(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        self.assertEqual(self.signature_information.is_signature_safe(request_body, signing_secret), True)

    def test_is_signature_safe_false(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7794"
        self.assertEqual(self.signature_information.is_signature_safe(request_body, signing_secret), False)
        
    

if __name__ == '__main__':
    unittest.main()