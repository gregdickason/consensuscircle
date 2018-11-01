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
             instruction0 = {"instructionHash":"85ceeddce78c021d6e55c8f3e422f7817df3f8f7e18c3db9dd5f0a100d1ede6d","sign":"YZSWn6QUtL7pCmzLTUBgFMudEwDbK567GU2jDUzRvofcLIdbNTziWrZOo0ybMG3AMWDJdodVyfmte46HIE9afQ==","instruction":{"source":"5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c","mostRecentBlockHeight":1,"slots":[{"wallet":"Default","payment":200000000,"action":"MinerFee","timeout":0},{"wallet":"Default","payment":0,"action":"Claim","target":"5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c","UpdateAction":"Identity.Citizenship.Type = South African","timeout":0},{"wallet":"Default","payment":500000000,"action":"ValidationRequest","target":"a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100","UpdateAction":"Identity.Citizenship.Type = South African","timeout":0}]}}
             
             instruction1 = {"instructionHash":"9dc2ec28e327dcedc0e168df7e9145e0dec5185015cdd0909b24db415ba659b8", "sign":"9d9pvXba+yJLiBiPC3r86BX/K6nYvNNzmYV0ybfne/DnTBiHCG+hqwz1R80AOZhfAGCSilyqn31oWsKcC7wsKw==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "f1199ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
             instruction2 = {"instructionHash":"dd9880075fa086e6025f6a01a4e2a9045ac751b5417045082668e5a9ca97c9c8", "sign":"jmUssEDe4yq4+Buqq4AbJub7zAQAOEfyWAd7g8TM1gdddThPGAyyjVie8XWX9kjfwlV4R3MN0xGIQh0582O6dQ==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "a1122ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
 
             instruction3 = {"instructionHash":"892d8844a61e38cdda9495026ece1b950f65cfcd0b1f8a0420ded163432bf5d7", "sign":"Zn6OiizVDvlbJVGqWsSlM+Rnw/S/+tTYIgg4KzNBJOtrfIooDJD5XJk2ViDzu0spUHvFcF2eEsjaAWDF974Xdg==", "instruction":{"source":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920", "someRandom": "b1199ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633", "slots": [{"wallet":0,"escrowAmount":200000,"action" : "update", "somethingelse to work out":"", "target":"abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)", "timeout":"timeInBlocksToAllow the next closest entity to update"}]}}
             instructionHandler0 = {"instructionHandlerHash":"b8af1c7b379903cbaf37e1213797c6412687c602be8e4e53d43fd022b6e74da2","sign":"utybCvxfiV9r9tHfDwX4H+KYhCAelUr4pK5BwRWRIjRiFq5DtvMrnZZrBe+JB5Csj1U9sJ904S3hpLiiTWG5UA==","instructionHandler":{"value":200, "owningEntity":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920",  "handlerScript":"limited by input script and allowed only to update the originating entity.  blah ).  If same for same entity - will have same hash and will override"}}
			
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
