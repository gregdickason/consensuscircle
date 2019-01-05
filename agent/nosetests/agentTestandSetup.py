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

    def test_105_process_genesisBlock_returns200(self):
             url = "http://localhost:5000/genesisBlock"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {'blockHash': '695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4'})

    def test_104_network_status_changes(self):
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

    def test_106_latest_block_initial(self):
             url = "http://localhost:5000/block"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {'lastBlock': '695e4a0c4f763fc95dfd6c29f334cc2eaf9c4a2bafcce09379b0864eda001eb4', 'circleDistance' : 0, 'blockHeight' : 0})

    def test_108_publish_block_then_latest_block(self):
             url = "http://localhost:5000/publishBlock"
             request = urllib.request.Request(url, data='{"blockID" : "34a3d75bdf70e43dc343bf28334736a66dc36283a292ebcf13d72e43b9a75c63"}'.encode('utf-8'))
             request.add_header("Content-Type","application/json")
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {"chainLength":1,"circleDistance":"561b3ab1b654de94aaa2d9d84335d74e3159968d29a47ff473788428be16210b028","error":"No error checking candidate block[]","lastBlock":"34a3d75bdf70e43dc343bf28334736a66dc36283a292ebcf13d72e43b9a75c63","message":"Block Conforms"})

             url = "http://localhost:5000/block"
             request = urllib.request.Request(url)
             response = urllib.request.urlopen(request)
             body = json.loads(response.read().decode('utf-8'))
             self.assertEqual(response.code, 200)
             self.assertEqual(body, {"blockHeight":1,"circleDistance":159526973199607193879304450923182459432912886055691720196950684421348839369257000,"lastBlock":"34a3d75bdf70e43dc343bf28334736a66dc36283a292ebcf13d72e43b9a75c63"})     


    def test_107_initialConfig(self):
        url = "http://localhost:5000/getConfig"
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        body = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.code, 200)
        self.assertEqual(body,{'agentIdentifier':'180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675','agentPrivateKey':'f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e','level':'founder','owner':'d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f','signedIdentifier':'30440220273835a615c5b40afcbd8774684ae3dad27a1c0cdc413789591f12dab0f5d4b0022061cf224c65ae3e4e1d09e34ccd5b861fcba5fd772cd7a00db10d51c632e57c36'})
