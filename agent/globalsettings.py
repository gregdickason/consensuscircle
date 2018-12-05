#!/usr/bin/python

class AgentSettings:
    def __init__(self):
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        self.maxAgentsInCircle = 4

        #default config settings
        # We have default settings we load on startup that get overridden by the appropriate setup call if signed correctly (
        self.agentIdentifier = "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675"
        self.agentPrivateKey = "f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e"
        self.ownerPublicKey = "04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f"
        self.signedIdentifier = "3046022100dfd1bd9c51c0a8f28db46198d15f302908b4e45067f33e0d851b8304a787bc44022100b4c1e9ec1146c8f120a952138750d16171affb8b9145c490e9463f2b94634bfb"
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

        self.instructionSet['Simple Transaction'] = '8292d2c55210392e3bb7c7e9c98c4d5cf4154431'
        self.instructionKeys['Simple Transaction'] = ['Payer Key', 'Receiver Key']
        self.instructionArgs['Simple Transaction'] = ['Payer Wallet', 'Receiver Wallet', 'Amount']


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
