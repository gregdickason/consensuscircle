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
            


    def test_120_process_firstBlock_returns200(self):
             url = "http://localhost:5000/blockPublished?blockID=1a044569fd3419c376356dedfc45989c8200dd64362cc9f4160e7aed9dc8a88a.json"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)

             #url = "http://localhost:5001/blockPublished?blockID=bcbb067aa59ce5ff1a56f33f229617db1bd3860488a02b8fd26b92d1b8d95fbe.json"
             #request = urllib.request.Request(url)
             #response = urllib.request.urlopen(request)
             #body = json.loads(response.read().decode('utf-8'))
             #self.assertEqual(response.code, 200)

             #url = "http://localhost:5002/blockPublished?blockID=bcbb067aa59ce5ff1a56f33f229617db1bd3860488a02b8fd26b92d1b8d95fbe.json"
             #request = urllib.request.Request(url)
             #response = urllib.request.urlopen(request)
             #body = json.loads(response.read().decode('utf-8'))
             #self.assertEqual(response.code, 200)

             #url = "http://localhost:5003/blockPublished?blockID=bcbb067aa59ce5ff1a56f33f229617db1bd3860488a02b8fd26b92d1b8d95fbe.json"
             #request = urllib.request.Request(url)
             #response = urllib.request.urlopen(request)
             #body = json.loads(response.read().decode('utf-8'))
             #self.assertEqual(response.code, 200)

             #url = "http://localhost:5005/blockPublished?blockID=bcbb067aa59ce5ff1a56f33f229617db1bd3860488a02b8fd26b92d1b8d95fbe.json"
             #request = urllib.request.Request(url)
             #response = urllib.request.urlopen(request)
             #body = json.loads(response.read().decode('utf-8'))
             #self.assertEqual(response.code, 200)
