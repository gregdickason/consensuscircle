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
             url = "http://localhost:5001/updateConfig"
             # TODO make this a jsonify request
             request = urllib.request.Request(url, data='{"ownerPKey":"a2e7623c29717a60913a2b36da830ab48da146eabd2453a0f0756630c25f5100","ownerLevel":"defender","agentIdentifier":"cb4d24f31f25703dd89fee5aa4813f55a16ce8d05d76af819e02b5c9f7ace7b2","signId":"VT1Jqo/zrrpNDP9AM+oc64JO9KAtQw1nFkWxaBUPa1qf3c6QqK8lxFn0252NokVuclqQnZKVaJr+HbQFDI8RQw==","agentPrivKey":"LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU9VNnRPT0ZLUXZ3NGttQy9VQzdUMkpwaGZkZmJJVGJiNlJ0ZGE2ZHFJYXFvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFckhyMDJiOHAzVklIK084VmhENkYzUjhGQmZUcWxmYjVPVjZwdDhWazhUait4MlNQOTV1Ywo3L28zZ0tyVlhiL29paTdWSjdsazcvRVdwVllaa0FrN1hBPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 201)

    def test_101_get_pkey_returns_200(self):
             url = "http://localhost:5001/PKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'the pkey of the agent is {body["pkey"]}')
             self.assertEqual(response.code, 200)
    
    def test_102_owner_returns_200(self):
             url = "http://localhost:5001/ownerPublicKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

    def test_103_level_returns_200(self):
             url = "http://localhost:5001/ownerLevel"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             
    def test_110_process_genesisBlock_returns200(self):
             url = "http://localhost:5001/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)


