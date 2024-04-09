import sys
import time
import unittest

from freeclimb.utils.request_verifier import RequestVerifier

class TestRequestVerifier(unittest.TestCase):
    """RequestVerifier unit test stubs"""

    def setUp(self):
        self.request_verifier = RequestVerifier()
    
    def tearDown(self):
        pass

    def test_check_request_body(self):
        request_body = ""
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 5 * 60 * 1000
        request_header = "t=1679944186,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Request Body cannot be empty or null")
    
    def test_check_request_header_no_signatures(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 5 * 60 * 1000
        request_header = "t=1679944186,"
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Error with request header, signatures are not present")
    
    def test_check_request_header_no_timestamp(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 5 * 60 * 1000
        request_header = "v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Error with request header, timestamp is not present")
    
    def test_check_request_header_empty_request_header(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 5 * 60 * 1000
        request_header = ""        
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Error with request header, Request header is empty")

    def test_check_signing_secret(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = ""
        tolerance = 5 * 60 * 1000
        request_header = "t=1679944186,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"        
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Signing secret cannot be empty or null")
    
    def test_check_tolerance_max_int(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = sys.maxsize
        request_header = "t=1679944186,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"        
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Tolerance value must be a positive integer")
    
    def test_check_tolerance_zero_value(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 0
        request_header = "t=1679944186,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"        
        with self.assertRaises(Exception) as exc:
            self.request_verifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Tolerance value must be a positive integer")
    
    def test_check_tolerance_negative_value(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = -5
        request_header = "t=1679944186,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"        
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Tolerance value must be a positive integer")
    
    def test_verify_tolerance(self):
        current_time = int(time.time())
        request_header_time = current_time - (6*60*1000)
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 5 * 60 * 1000
        request_header = "t=" + str(request_header_time) + ",v1=1d798c86e977ff734dec3a8b8d67fe8621dcc1df46ef4212e0bfe2e122b01bfd,v1=78e363373f8a9f6fddc2e3ca3a1ed9dc94efa44d378363adf52434e78f32d8fb"        
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Request time exceeded tolerance threshold. Request: " + str(request_header_time)
                + ", CurrentTime: " + str(current_time) + ", tolerance: " + str(tolerance))
    
    def test_verify_signature(self):
        current_time = int(time.time())
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7794"
        tolerance = 5 * 60 * 1000
        request_header = "t=" + str(current_time) + ",v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=1ba18712726898fbbe48cd862dd096a709f7ad761a5bab14bda9ac24d963a6a8"        
        with self.assertRaises(Exception) as exc:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        self.assertEqual(str(exc.exception), "Unverified signature request, If this request was unexpected, it may be from a bad actor. Please proceed with caution. If the request was exepected, please check any typos or issues with the signingSecret")
    
    def test_verify_request_signature(self):
        request_body = "{\"accountId\":\"AC1334ffb694cd8d969f51cddf5f7c9b478546d50c\",\"callId\":\"CAccb0b00506553cda09b51c5477f672a49e0b2213\",\"callStatus\":\"ringing\",\"conferenceId\":null,\"direction\":\"inbound\",\"from\":\"+13121000109\",\"parentCallId\":null,\"queueId\":null,\"requestType\":\"inboundCall\",\"to\":\"+13121000096\"}"
        signing_secret = "sigsec_ead6d3b6904196c60835d039e91b3341c77a7793"
        tolerance = 5 * 60 * 1000
        request_header = "t=3795106129,v1=c3957749baf61df4b1506802579cc69a74c77a1ae21447b930e5a704f9ec4120,v1=96b769b34426fa69117dd6d1bda2c432beb2cf4c63dd2de495fca0c37dde82b2"        
        raised = False
        try:
            RequestVerifier.verify_request_signature(request_body, request_header, signing_secret, tolerance)
        except:
            raised = True
            self.assertFalse(raised, 'Exception has been raised')
        
    
    

if __name__ == '__main__':
    unittest.main()