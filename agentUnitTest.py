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
    
    #GREG HERE
    
    def test_flask_application_is_up_and_running(self):
          url = "http://www.google.com"
          request = urllib.request.Request(url)
          response = urllib.request.urlopen(request)
          self.assertEqual(response.code, 200)
          
    
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
    
    
    def test_converge_returns_200(self):
          url = "http://localhost:5000/converge"
          request = urllib.request.Request(url)
          response = urllib.request.urlopen(request)
          self.assertEqual(response.code, 200)


    def test_instruction_returns_201(self):
          url = "http://localhost:5000/instruction"
          request = urllib.request.Request(url, data='{"sender":"the Greg","recipient":"gatlandFF","hash":"AD34BBAF"}'.encode('utf-8'))
          request.add_header("Content-Type","application/json")
          response = urllib.request.urlopen(request)
          self.assertEqual(response.code, 201)



    def test_register_returns_201(self):
          url = "http://localhost:5000/agents/register"
          request = urllib.request.Request(url, data='{"agents":["http://localhost:5001"]}'.encode('utf-8'))
          request.add_header("Content-Type","application/json")
          response = urllib.request.urlopen(request)
          self.assertEqual(response.code, 201)
  