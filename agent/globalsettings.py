#!/usr/bin/python

class AgentSettings:
    def __init__(self):
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        self.maxAgentsInCircle = 4

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

        self.instructionSet['hello'] = '3b54771cde78c3995cd6620fe0d9b9233c6214ca'
        self.instructionKeys['hello'] = []
        self.instructionArgs['hello'] = []

        self.instructionSet['UIDummy'] = "fakehash"
        self.instructionKeys['UIDummy'] = ['test 1', 'test 2']
        self.instructionArgs['UIDummy'] = ['cameron', 'greg']

        # TODO - add ARGS[1] and KEYS[1] to payment
        self.instructionSet['Simple Transaction'] = '7e143676e29910dda0c063dae24fb76c65e8e6cc'
        self.instructionKeys['Simple Transaction'] = ['Receiver Key']
        self.instructionArgs['Simple Transaction'] = ['Payer Wallet', 'Receiver Wallet', 'Amount']

        self.instructionSet['Payment'] = 'dff9573863a715b71013092edf59a18f9abae685'
        self.instructionKeys['Payment'] = ['Originator Key', 'Payer Key', 'Receiver Key']
        # TODO - put in blockheight in all instructions at argument 3 for rollback.
        self.instructionArgs['Payment'] = ['Mining State', 'InstructionHash', 'Blockheight', 'Wallet Payer', 'Wallet Receiver','Payment Amount','instructionFee']

        self.instructionSet['resetdb'] = "24c57e46b57bb710c3f61e0249e3771f40327fe6"
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
