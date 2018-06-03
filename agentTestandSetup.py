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
    def test_100_pkey_returns_201(self):
              url = "http://localhost:5000/setPKey"
              request = urllib.request.Request(url, data='{"pkey":"9c8345cf13413cd0ff0e6af4f33cce4f0555fb3a50364b64265b05ce134af28d"}'.encode('utf-8'))
              request.add_header("Content-Type","application/json")
              response = urllib.request.urlopen(request)
              self.assertEqual(response.code, 201)

    def test_101_get_pkey_returns_200(self):
             url = "http://localhost:5000/PKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'the pkey of the agent is {body["pkey"]}')
             self.assertEqual(response.code, 200)
    
    def test_102_owner_returns_200(self):
             url = "http://localhost:5000/ownerPublicKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

    def test_103_level_returns_200(self):
             url = "http://localhost:5000/ownerLevel"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             
    def test_110_process_genesisBlock_returns200(self):
             url = "http://localhost:5000/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)


