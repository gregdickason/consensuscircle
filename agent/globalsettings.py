#!/usr/bin/python

class AgentSettings:
    def __init__(self):
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        self.maxAgentsInCircle = 4

        #default config settings
        # We have default settings we load on startup that get overridden by the appropriate setup call if signed correctly (
        self.agentIdentifier = "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675"
        self.agentPrivateKey = "f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e"
        self.agentPublicKey = "04ae5e9fba406e2529f979fbfb98bcffb5c390864f8cb5248161bcfee296b2827c63f364f780463d952665c8a892ec2570cc16af5f309f8eac6466439a93a8466f"
        self.ownerID = "d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f"
        self.signedIdentifier = "30440220273835a615c5b40afcbd8774684ae3dad27a1c0cdc413789591f12dab0f5d4b0022061cf224c65ae3e4e1d09e34ccd5b861fcba5fd772cd7a00db10d51c632e57c36"
        self.level = "founder"

class blockSettings:
    def __init__(self):
        #TODO fill this
        self.blockKeys = ['nextBlock', 'previousBlock', 'outputMatrix', 'filePath']

class instructionInfo:
    def __init__(self):
        self.instructionSet = {}
        self.instructionKeys = {}
        self.instructionArgs = {}
        
        # all instructions have a similar set:
        # args[0] is either 'mining' or 'mined' to show lua how to process it (update state)
        # keys[0] is the entity / owner / agent id of the originator
        # this is automatically input (not in the instruction itself. 
        
        

        self.instructionSet['hello'] = '59f3eb590a68c71483463553f9b2d715550be5ae'
        self.instructionKeys['hello'] = []
        self.instructionArgs['hello'] = []

        self.instructionSet['UIDummy'] = "fakehash"
        self.instructionKeys['UIDummy'] = ['test 1', 'test 2']
        self.instructionArgs['UIDummy'] = ['cameron', 'greg']

        self.instructionSet['Simple Transaction'] = '8292d2c55210392e3bb7c7e9c98c4d5cf4154431'
        self.instructionKeys['Simple Transaction'] = ['Payer Key', 'Receiver Key']
        self.instructionArgs['Simple Transaction'] = ['Payer Wallet', 'Receiver Wallet', 'Amount']
        
        self.instructionSet['Payment'] = 'cbf23b37ecf8e312fbb5260151705a0b17da5d29'
        self.instructionKeys['Payment'] = ['Originator Key', 'Payer Key', 'Receiver Key']
        self.instructionArgs['Payment'] = ['Mining State', 'InstructionHash', 'Wallet Payer', 'Wallet Receiver','Payment Amount','Blockheight','instructionFee']
        
        self.instructionSet['resetdb'] = "a7d47714f78aff4d339f66ea99d520e66df80f5d"
        self.instructionKeys['resetdb'] = []
        self.instructionArgs['resetdb'] = []


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
