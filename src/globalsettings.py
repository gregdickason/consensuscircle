#!/usr/bin/python

class AgentSettings:
    def __init__(self):
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        self.maxAgentsInCircle = 4

        #default config settings
        # We have default settings we load on startup that get overridden by the appropriate setup call if signed correctly (
        self.agentIdentifier = "17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920",
        self.agentPrivateKey = "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSVBsOXp4ZTIwT254QmJaR2F6ZHdKS2xWZW5kRnFkZTZmY05acnU2MFV3cWVvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFcmw2ZnVrQnVKU241ZWZ2N21Mei90Y09RaGsrTXRTU0JZYnorNHBheWdueGo4MlQzZ0VZOQpsU1pseUtpUzdDVnd6QmF2WHpDZmpxeGtaa09hazZoR2J3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=",
        self.ownerPKey = "5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c",
        self.signedIdentifier = "amT6nlrsler57PrP+QfDfSOvhNeE76IRnc3at3ODmvUZe9IsvwM010K44Uv21+HqrXK14oSkhNSSBave0LFW3g==",
        self.level = "founder"
