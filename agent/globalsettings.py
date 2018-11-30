#!/usr/bin/python

class AgentSettings:
    def __init__(self):
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        self.maxAgentsInCircle = 4

        #default config settings
        # We have default settings we load on startup that get overridden by the appropriate setup call if signed correctly (
        self.agentIdentifier = "17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920"
        self.agentPrivateKey = "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSVBsOXp4ZTIwT254QmJaR2F6ZHdKS2xWZW5kRnFkZTZmY05acnU2MFV3cWVvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFcmw2ZnVrQnVKU241ZWZ2N21Mei90Y09RaGsrTXRTU0JZYnorNHBheWdueGo4MlQzZ0VZOQpsU1pseUtpUzdDVnd6QmF2WHpDZmpxeGtaa09hazZoR2J3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="
        self.ownerPKey = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFcmw2ZnVrQnVKU241ZWZ2N21Mei90Y09RaGsrTQp0U1NCWWJ6KzRwYXlnbnhqODJUM2dFWTlsU1pseUtpUzdDVnd6QmF2WHpDZmpxeGtaa09hazZoR2J3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
        self.signedIdentifier = "amT6nlrsler57PrP+QfDfSOvhNeE76IRnc3at3ODmvUZe9IsvwM010K44Uv21+HqrXK14oSkhNSSBave0LFW3g=="
        self.level = "founder"

class instructionInfo:
    def __init__(self):
        self.instructionSet = {}
        self.instructionKeys = {}
        self.instructionArgs = {}

        self.instructionSet['hello'] = '59f3eb590a68c71483463553f9b2d715550be5ae'
        self.instructionKeys['hello'] = []
        self.instructionArgs['hello'] = []

        self.instructionSet['UIDummy'] = "fakehash"
        self.instructionKeys['UIDummy'] = ['test 1', 'test 2']
        self.instructionArgs['UIDummy'] = ['cameron', 'greg']

    def getInstructionHash(self, name):
        if name in self.instructionSet.keys():
            return self.instructionSet[name]
        else:
            return None

    def getInstructionKeys(self, name):
        if name in self.instructionKeys.keys():
            return self.instructionKeys[name]
        else:
            return None

    def getInstructionArgs(self, name):
        if name in self.instructionArgs.keys():
            return self.instructionArgs[name]
        else:
            return None

    def getInstructionNames(self):
        return list(self.instructionSet.keys())
