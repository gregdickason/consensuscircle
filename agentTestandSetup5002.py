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
             url = "http://localhost:5002/updateConfig"
             # TODO make this a jsonify request
             request = urllib.request.Request(url, data='{"ownerPKey":"1874d743da77d67793e424958b06262daa3eefb2ea15fe64b6e646879ad5118d","ownerLevel":"protector","agentIdentifier":"5cbda1c61193fbd4644eeca3d9d5d6572ab8ac3399dcdcfa7241dcab509d2102","signId":"clzVbCbKVCfYDUhNf7WbG1E7bmxXihrp5Or31A0Lr3EKJ5F4YD1XBQwLhF7oRuTaf3FZbtkBd1heVyyHFyH2Hg==","agentPrivKey":"LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUxCK0w1SGljQzhaU1RIcm1kaUpFVXNKMzlOZG4yOHYwRTF2MzRMVVRGcDZvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFckpkN1FtSm1WUWIxdUttNlEvTytCWXFZWWhyNElHaFNub3c5eFlGeS8rTTgxZHNVaVVGbAp5MG4rMjJEZkpWQlpRMnZyT3JJRU9tRWtrODBoRGR0UmRnPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 201)

    def test_101_get_pkey_returns_200(self):
             url = "http://localhost:5002/PKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'the pkey of the agent is {body["pkey"]}')
             self.assertEqual(response.code, 200)
    
    def test_102_owner_returns_200(self):
             url = "http://localhost:5002/ownerPublicKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

    def test_103_level_returns_200(self):
             url = "http://localhost:5002/ownerLevel"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             
    def test_110_process_genesisBlock_returns200(self):
             url = "http://localhost:5002/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

