import json

# For simulation purposes we dont care about instructions or validity just the output of the random vector that will be the root for the next block (determine participants)
class lastBlock:
    def __init__(self):
        with open('newBlock.json') as json_data:
            self.block = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
        print(f'New Block is {self.block}')
        self.outputMatrix = self.block['blockRandomMatrix']
        self.consensusCircle = self.block['consensusCircle']
        self.instructionCount = self.block['blockInstructionCount']
        self.merkleTreeRoot = self.block['blockMerkleRoot']  # Random for simulation 
        self.blockHash = self.block['blockHash']   # Hash of this block
        self.previousBlock = self.block['previousBlock']
        self.blockHeight = self.block['blockHeight']
        self.circleDistance = 0
        
        