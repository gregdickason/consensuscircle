import urllib.request
import json
from flask import Flask
from flask_testing import TestCase 

# Methods for setting up and executing the simulation for consensus circle.  This is the test harness that calls all the nodes and starts the 
# convergence after first seeding instructions and registering nodes with each other.
# It calls convergence protocol in order: converge instructions, converge hashed vector, converge full vector, generate block

class TddAgent(TestCase):
    
    
    # if the create_app is not implemented NotImplementedError will be raised
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app         
    
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
    
    def test_add_instructions_to_agents(self):
          # do this through a text file in future
          url1 = "http://localhost:5000/instruction"
          url2 = "http://localhost:5001/instruction"
          url3 = "http://localhost:5002/instruction"
          url4 = "http://localhost:5003/instruction"
          url5 = "http://localhost:5004/instruction"
          request11 = urllib.request.Request(url1, data='{"sender":"sender1","recipient":"recipient1","hash":"12345"}'.encode('utf-8'))
          request11.add_header("Content-Type","application/json")
          request12 = urllib.request.Request(url1, data='{"sender":"sender2","recipient":"recipient1","hash":"23456"}'.encode('utf-8'))
          request12.add_header("Content-Type","application/json")
          request21 = urllib.request.Request(url2, data='{"sender":"sender3","recipient":"recipient1","hash":"34567"}'.encode('utf-8'))
          request21.add_header("Content-Type","application/json")
          request22 = urllib.request.Request(url2, data='{"sender":"sender4","recipient":"recipient1","hash":"45678"}'.encode('utf-8'))
          request22.add_header("Content-Type","application/json")
          request31 = urllib.request.Request(url3, data='{"sender":"sender5","recipient":"recipient1","hash":"56789"}'.encode('utf-8'))
          request31.add_header("Content-Type","application/json")
          request32 = urllib.request.Request(url3, data='{"sender":"sender6","recipient":"recipient2","hash":"67891"}'.encode('utf-8'))
          request32.add_header("Content-Type","application/json")
          request41 = urllib.request.Request(url4, data='{"sender":"sender7","recipient":"recipient2","hash":"78912"}'.encode('utf-8'))
          request41.add_header("Content-Type","application/json")
          request42 = urllib.request.Request(url4, data='{"sender":"sender8","recipient":"recipient2","hash":"89123"}'.encode('utf-8'))
          request42.add_header("Content-Type","application/json")
          request51 = urllib.request.Request(url5, data='{"sender":"sender9","recipient":"recipient2","hash":"91234"}'.encode('utf-8'))
          request51.add_header("Content-Type","application/json")
          request52 = urllib.request.Request(url5, data='{"sender":"sender10","recipient":"recipient2","hash":"11234"}'.encode('utf-8'))
          request52.add_header("Content-Type","application/json")
          
          response = urllib.request.urlopen(request11)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request12)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request21)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request22)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request31)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request32)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request41)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request42)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request51)
          self.assertEqual(response.code, 201)
          response = urllib.request.urlopen(request52)
          self.assertEqual(response.code, 201)

    

    # Register agents with each other for the convergence protocol to execute
    def test_register_returns_201(self):
          # do this through text file to test fully connected, partially connected and sparsely connected scenarios. 
          url1 = "http://localhost:5000/agents/register"
          url2 = "http://localhost:5001/agents/register"
          url3 = "http://localhost:5002/agents/register"
          url4 = "http://localhost:5003/agents/register"
          url5 = "http://localhost:5004/agents/register"
          
          request1 = urllib.request.Request(url1, data='{"agents":["http://localhost:5001","http://localhost:5002"]}'.encode('utf-8'))
          request1.add_header("Content-Type","application/json")
          
          request2 = urllib.request.Request(url2, data='{"agents":["http://localhost:5002","http://localhost:5003"]}'.encode('utf-8'))
          request2.add_header("Content-Type","application/json")
          
          request3 = urllib.request.Request(url3, data='{"agents":["http://localhost:5003","http://localhost:5004"]}'.encode('utf-8'))
          request3.add_header("Content-Type","application/json")
          
          request4 = urllib.request.Request(url4, data='{"agents":["http://localhost:5004","http://localhost:5000"]}'.encode('utf-8'))
          request4.add_header("Content-Type","application/json")
          
          request5 = urllib.request.Request(url5, data='{"agents":["http://localhost:5000","http://localhost:5001"]}'.encode('utf-8'))
          request5.add_header("Content-Type","application/json")
          
          
          response = urllib.request.urlopen(request1)
          self.assertEqual(response.code, 201)
          
          response = urllib.request.urlopen(request2)
          self.assertEqual(response.code, 201)
          
          response = urllib.request.urlopen(request3)
          self.assertEqual(response.code, 201)
          
          response = urllib.request.urlopen(request4)
          self.assertEqual(response.code, 201)
          
          response = urllib.request.urlopen(request5)
          self.assertEqual(response.code, 201)
          
    
    # loop on converging uids
    def test_run_converge_uids_returns_200and202(self):
             url1 = "http://localhost:5000/convergeUIDs"
             url2 = "http://localhost:5001/convergeUIDs"
             url3 = "http://localhost:5002/convergeUIDs"
             url4 = "http://localhost:5003/convergeUIDs"
             url5 = "http://localhost:5004/convergeUIDs"
             
             
             # loop while still seeing 202s, error if any non 200, 202 or loop too long (more than 5)
             GREG HERE
             request = urllib.request.Request(url1)
             response = urllib.request.urlopen(request)
             if response.code == 202:
             
             self.assertEqual(response.code, 200)
             
             request = urllib.request.Request(url2)
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)
             
             request = urllib.request.Request(url3)
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)
             
             request = urllib.request.Request(url4)
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)
             
             request = urllib.request.Request(url5)
             response = urllib.request.urlopen(request)
             self.assertEqual(response.code, 200)

    
    
    def test_run_converge_instructions_returns_200(self):
         url1 = "http://localhost:5000/convergeInstructions"
         url2 = "http://localhost:5001/convergeInstructions"
         url3 = "http://localhost:5002/convergeInstructions"
         url4 = "http://localhost:5003/convergeInstructions"
         url5 = "http://localhost:5004/convergeInstructions"
         
         request = urllib.request.Request(url1)
         response = urllib.request.urlopen(request)
         self.assertEqual(response.code, 200)
         
         request = urllib.request.Request(url2)
         response = urllib.request.urlopen(request)
         self.assertEqual(response.code, 200)
         
         request = urllib.request.Request(url3)
         response = urllib.request.urlopen(request)
         self.assertEqual(response.code, 200)
         
         request = urllib.request.Request(url4)
         response = urllib.request.urlopen(request)
         self.assertEqual(response.code, 200)
         
         request = urllib.request.Request(url5)
         response = urllib.request.urlopen(request)
         self.assertEqual(response.code, 200)

    
    def test_run_converge_random_matrix_hash_returns_200(self):
         pass
    
    
    def test_run_converge_random_matrix_returns_200(self):
         pass
    
    
    
    
    def test_run_convergence_returns_200(self):
         pass 

    