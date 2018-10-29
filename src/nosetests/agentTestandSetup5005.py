import urllib.request
import json
from flask import Flask
from flask_testing import TestCase 

class TddAgent(TestCase):
        
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
    def test_100_updateConfig_returns_201(self):
             url = "http://localhost:5005/updateConfig"
             # TODO make this a jsonify request
             request = urllib.request.Request(url, data='{"ownerPKey":"b2544ad676c98dc7c5943abd5137737555e4ee0c028cd5ef1bc7ad85be381a7f","ownerLevel":"contributor","agentIdentifier":"66702543e7983626b4e193d4aa8e3ee8c8f1439a1707a91ad45719ad2945c8a6","signId":"/SUmdEvzoSFuRnRmCw4Id7wpRz/In52648ZShy6UnRtPUZJWDF3hcvvIqnUQ9wtZfBktiKLFRECJAqdZZDRCeQ==","agentPrivKey":"LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUFSajFkazBkZVR0UlRqK3ZRMVVmZE10N2hib3BkblNWOGpyRXkzU25TYndvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFaW5NWnBwUlozanlGeDdxbXEvSDdldnpDdGRlNXR4cmJkNzNZUVk1OGpaR0xRS1Vxa25BQgpFN2U4QU4zYmJuWkQ4czYzdzZGdGRPTWpNVTdSb0RXb21nPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 201)

    def test_101_get_pkey_returns_200(self):
             url = "http://localhost:5005/PKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'the pkey of the agent is {body["pkey"]}')
             self.assertEqual(response.code, 200)
    
    def test_102_owner_returns_200(self):
             url = "http://localhost:5005/ownerPublicKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

    def test_103_level_returns_200(self):
             url = "http://localhost:5005/ownerLevel"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             
    def test_110_process_genesisBlock_returns200(self):
             url = "http://localhost:5005/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
 