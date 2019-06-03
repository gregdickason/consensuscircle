#!/usr/bin/python

class AgentSettings:
    def __init__(self):
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        self.maxAgentsInCircle = 4


# TODO: remove and test.  Add in a validate block on receiving block
class blockSettings:
    def __init__(self):
        #TODO fill this
        self.blockKeys = ['nextBlock', 'previousBlock', 'outputMatrix', 'filePath']
