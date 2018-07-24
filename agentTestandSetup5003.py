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
             url = "http://localhost:5003/updateConfig"
             # TODO make this a jsonify request
             request = urllib.request.Request(url, data='{"ownerPKey":"dd1139e8c1b85e1488346d07c40a58013e73d2b91b104bcddc0bcff85d0b6ae7","ownerLevel":"contributor","agentIdentifier":"f3d15dbd57deb8320663ebb5afa905ee2458445e6ab512911f39f9eea9a6f89c","signId":"6/tRQRg+ZZUDYblgn1dFT5Z4HrJNaxWkP0xO4n0Zvr2J+irkyZG84lLnGTCIIdEtw3uv3vDIa2Yljz77imeYog==","agentPrivKey":"LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUVNTGRvYlUzczZGTG8wbzNkZ21tTHpRMndDN21HdjdweDY1c0NpT0NmUm5vQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFZGtyOVpORSswR2JnOHNnZW9Hb1ZPSjdFTzhVd1Byei9QaUVzTVJEVnVwT3YxdFpVYUNHVgozaSsxa01tWlA4c3dBUm03WVJMMVlKTWZUdUl3Tks5K1d3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 201)

    def test_101_get_pkey_returns_200(self):
             url = "http://localhost:5003/PKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'the pkey of the agent is {body["pkey"]}')
             self.assertEqual(response.code, 200)
    
    def test_102_owner_returns_200(self):
             url = "http://localhost:5003/ownerPublicKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

    def test_103_level_returns_200(self):
             url = "http://localhost:5003/ownerLevel"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             
    def test_110_process_genesisBlock_returns200(self):
             url = "http://localhost:5003/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
