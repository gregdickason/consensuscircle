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
    def test_101_get_pkey_returns_200(self):
             url = "http://localhost:5000/getPrivateKey"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
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
             self.assertEqual(body, {'ownerLevel' : 'founder'})

    def test_110_process_genesisBlock_returns200(self):
             url = "http://localhost:5000/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {'blockHash': '695E4A0C4F763FC95DFD6C29F334CC2EAF9C4A2BAFCCE09379B0864EDA001EB4'})

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

    def test_latest_block_initial(self):
             url = "http://localhost:5000/block"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {'lastBlock': '695E4A0C4F763FC95DFD6C29F334CC2EAF9C4A2BAFCCE09379B0864EDA001EB4', 'circleDistance' : 0, 'blockHeight' : 0})

    # def test_publish_block_then_latest_block(self):
    #          url = "http://localhost:5000/publishBlock"
    #          request = urllib.request.Request(url, data='{"blockID" : "bcbb067aa59ce5ff1a56f33f229617db1bd3860488a02b8fd26b92d1b8d95fbe.json"}'.encode('utf-8'))
    #          request.add_header("Content-Type","application/json")
    #          response = urllib.request.urlopen(request)
    #          body = json.loads(response.read().decode('utf-8'))
    #          self.assertEqual(response.code, 200)
    #          self.assertEqual(body, {'chainLength': 1, 'circleDistance' : 'dc1ccc6bb8169fe29a332b54247ea2a0ca621039518ea994ff14a418d2daf5a8e3', 'lastBlock' : '72e055253cf8c78d8fc582b4f2e43ec001c564cbdfb3c361c5d0e2adfbebbffd'})
    #
    #          url = "http://localhost:5000/block"
    #          request = urllib.request.Request(url)
    #          response = urllib.request.urlopen(request)
    #          body = json.loads(response.read().decode('utf-8'))
    #          self.assertEqual(response.code, 200)
    #          self.assertEqual(body, {'lastBlock': '72e055253cf8c78d8fc582b4f2e43ec001c564cbdfb3c361c5d0e2adfbebbffd', 'circleDistance' : 'dc1ccc6bb8169fe29a332b54247ea2a0ca621039518ea994ff14a418d2daf5a8e3', 'blockHeight' : 1})

    def test_a_initialConfig(self):
        url = "http://localhost:5000/getConfig"
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        body = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.code, 200)
        self.assertEqual(body, {'level': 'founder', 'agentIdentifier' : '180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675', 'owner' : '04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f', 'signedIdentifier' : '3046022100dfd1bd9c51c0a8f28db46198d15f302908b4e45067f33e0d851b8304a787bc44022100b4c1e9ec1146c8f120a952138750d16171affb8b9145c490e9463f2b94634bfb', 'agentPrivateKey' : 'f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e'})


    def test_initial_config_and_adjust(self):
            url = "http://localhost:5000/getConfig"
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            body = json.loads(response.read().decode('utf-8'))
            self.assertEqual(response.code, 200)
            self.assertEqual(body, {'level': 'founder', 'agentIdentifier' : '180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675', 'owner' : '04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f', 'signedIdentifier' : '3046022100dfd1bd9c51c0a8f28db46198d15f302908b4e45067f33e0d851b8304a787bc44022100b4c1e9ec1146c8f120a952138750d16171affb8b9145c490e9463f2b94634bfb', 'agentPrivateKey' : 'f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e'})

            url = "http://localhost:5000/updateConfig"
            request = urllib.request.Request(url, data='{"level" : "4", "agentIdentifier" : "5", "owner" : "cameron", "signedIdentifier" : "signature", "agentPrivateKey" : "test:"}'.encode('utf-8'))
            request.add_header("Content-Type","application/json")
            response = urllib.request.urlopen(request)
            body = json.loads(response.read().decode('utf-8'))
            self.assertEqual(response.code, 201)
            self.assertEqual(body, {'message': 'Updated agent config'})

            url = "http://localhost:5000/getConfig"
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            body = json.loads(response.read().decode('utf-8'))
            self.assertEqual(response.code, 200)
            self.assertEqual(body, {'level': '4', 'agentIdentifier' : '5', 'owner' : 'cameron', 'signedIdentifier' : 'signature', 'agentPrivateKey' : 'test:'})

            url = "http://localhost:5000/updateConfig"
            request = urllib.request.Request(url, data='{"level": "founder", "agentIdentifier" : "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675", "owner" : "04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f", "signedIdentifier" : "3046022100dfd1bd9c51c0a8f28db46198d15f302908b4e45067f33e0d851b8304a787bc44022100b4c1e9ec1146c8f120a952138750d16171affb8b9145c490e9463f2b94634bfb", "agentPrivateKey" : "f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e"}'.encode('utf-8'))
            request.add_header("Content-Type","application/json")
            response = urllib.request.urlopen(request)
            body = json.loads(response.read().decode('utf-8'))
            self.assertEqual(response.code, 201)
            self.assertEqual(body, {'message': 'Updated agent config'})

            url = "http://localhost:5000/getConfig"
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            body = json.loads(response.read().decode('utf-8'))
            self.assertEqual(response.code, 200)
            self.assertEqual(body, {'level': 'founder', 'agentIdentifier' : '180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675', 'owner' : '04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f', 'signedIdentifier' : '3046022100dfd1bd9c51c0a8f28db46198d15f302908b4e45067f33e0d851b8304a787bc44022100b4c1e9ec1146c8f120a952138750d16171affb8b9145c490e9463f2b94634bfb', 'agentPrivateKey' : 'f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e'})
