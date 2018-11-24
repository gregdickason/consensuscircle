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
             url = "http://localhost:5000/updateConfig"
             # TODO make this a jsonify request
             request = urllib.request.Request(url, data='{"owner":"5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c","level":"founder","agentIdentifier":"17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920","signedIdentifier":"amT6nlrsler57PrP+QfDfSOvhNeE76IRnc3at3ODmvUZe9IsvwM010K44Uv21+HqrXK14oSkhNSSBave0LFW3g==","agentPrivateKey":"LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSVBsOXp4ZTIwT254QmJaR2F6ZHdKS2xWZW5kRnFkZTZmY05acnU2MFV3cWVvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFcmw2ZnVrQnVKU241ZWZ2N21Mei90Y09RaGsrTXRTU0JZYnorNHBheWdueGo4MlQzZ0VZOQpsU1pseUtpUzdDVnd6QmF2WHpDZmpxeGtaa09hazZoR2J3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="}'.encode('utf-8'))
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

    def test_network_status_changes(self):
             url = "http://localhost:5000/getNetworkStatus"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(body, {'network': 'on'})
             self.assertEqual(response.code, 200)

             url = "http://localhost:5000/setNetworkStatus"
             request = urllib.request.Request(url, data='{"network" : "off"}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {'networkOn': 'False'})

             url = "http://localhost:5000/getNetworkStatus"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(body, {'network': 'off'})
             self.assertEqual(response.code, 200)

             url = "http://localhost:5000/setNetworkStatus"
             request = urllib.request.Request(url, data='{"network" : "on"}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {'networkOn': 'True'})

             url = "http://localhost:5000/getNetworkStatus"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(body, {'network': 'on'})
             self.assertEqual(response.code, 200)
