import urllib.request
import json
from flask import Flask
from flask_testing import TestCase 

class TddAgent(TestCase):
    # used to setup for a block - adds instructions and instruction handlers that can be parsed.  
    #  All sent to the same agent as assumption is we are in emulation so this is emulating the block production
    
    # used https://damyanon.net/post/flask-series-testing/ to understand how to set up unit testing of flask applications
    # if the create_app is not implemented NotImplementedError will be raised
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app 
    
    #TODO: test response body and what is returned is what is expected (not just the return codes)
    
    #def dont_test_flask_application_is_up_and_running(self):
    #      url = "http://www.google.com"
    #      request = urllib.request.Request(url)
    #      response = urllib.request.urlopen(request)
    #      self.assertEqual(response.code, 200)
          
    
    @classmethod
    def setUpClass(cls):
        pass
        
    
    @classmethod
    def tearDownUpClass(cls):
        pass
    
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
            
    # Order is important to allow population of state.  Use numbering from 100 in the test names to ensure the order we need
    def test_100_populateInstructions_200(self):
             url0 = "http://localhost:5000/instruction"
             urlh = "http://localhost:5000/instructionHandler"
             
             
             # instruction 0,1, 2 to all agents, others to less
             instruction0 = {"instructionHash":"5908a04a072f0beb2d7521bb9ec77662234c4a8ccb44d4e15541e91952380938", "sign":"AlqYGbLCR7YbDcuBEd6vlaDYCsuF1Hro+EuJG6st7Q4YpOoIxrRVZU8JWF53+q1/U9O4fQZg9WZMDH97sBvCLg==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "e1148ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
             instruction1 = {"instructionHash":"9dc2ec28e327dcedc0e168df7e9145e0dec5185015cdd0909b24db415ba659b8", "sign":"AlqYGbLCR7YbDcuBEd6vlaDYCsuF1Hro+EuJG6st7Q4YpOoIxrRVZU8JWF53+q1/U9O4fQZg9WZMDH97sBvCLg==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "f1199ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
             instruction2 = {"instructionHash":"dd9880075fa086e6025f6a01a4e2a9045ac751b5417045082668e5a9ca97c9c8", "sign":"AlqYGbLCR7YbDcuBEd6vlaDYCsuF1Hro+EuJG6st7Q4YpOoIxrRVZU8JWF53+q1/U9O4fQZg9WZMDH97sBvCLg==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "a1122ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
 
             instruction3 = {"instructionHash":"892d8844a61e38cdda9495026ece1b950f65cfcd0b1f8a0420ded163432bf5d7", "sign":"AlqYGbLCR7YbDcuBEd6vlaDYCsuF1Hro+EuJG6st7Q4YpOoIxrRVZU8JWF53+q1/U9O4fQZg9WZMDH97sBvCLg==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "b1199ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
             instructionHandler0 = {"instructionHandlerHash":"b8af1c7b379903cbaf37e1213797c6412687c602be8e4e53d43fd022b6e74da2","sign":"AlqYGbLCR7YbDcuBEd6vlaDYCsuF1Hro+EuJG6st7Q4YpOoIxrRVZU8JWF53+q1/U9O4fQZg9WZMDH97sBvCLg==","instructionHandler":{"value":200, "owningEntity":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920",  "handlerScript":"limited by input script and allowed only to update the originating entity.  blah ).  If same for same entity - will have same hash and will override"}}
			
             request = urllib.request.Request(url0, json.dumps(instruction0).encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)
             
             request = urllib.request.Request(url0, json.dumps(instruction1).encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(url0, json.dumps(instruction2).encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(url0, json.dumps(instruction3).encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(urlh, json.dumps(instructionHandler0).encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)
