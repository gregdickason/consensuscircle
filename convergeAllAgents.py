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
    def test_100_populateInstructions_200(self):
             url0 = "http://localhost:5000/converge"
             url1 = "http://localhost:5001/converge"
             url2 = "http://localhost:5002/converge"
             url3 = "http://localhost:5003/converge"
             url5 = "http://localhost:5005/converge"
             
             
             request = urllib.request.Request(url0)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'The convergenced Agents are {body["agents"]}')
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(url1)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'The convergenced Agents are {body["agents"]}')
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(url2)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'The convergenced Agents are {body["agents"]}')
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(url3)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'The convergenced Agents are {body["agents"]}')
             self.assertEqual(response.code, 200)

             request = urllib.request.Request(url5)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             print(f'The convergenced Agents are {body["agents"]}')
             self.assertEqual(response.code, 200)
