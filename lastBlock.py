import json

# For simulation purposes we dont care about instructions or validity just the output of the random vector that will be the root for the next block (determine participants)
class lastBlock:
    def __init__(self):
        with open('previousblock.json') as json_data:
            self.block = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
        print(f'PreviousBlock is {self.block}')
        self.outputMatrix = self.block['blockRandomMatrix']
        self.merkleTreeRoot = self.block['blockMerkleRoot']  # Random for simulation 
        self.blockHash = self.block['blockHash']   # Hash of this block
        self.previousBlock = self.block['previousBlock']
        self.blockHeight = self.block['blockHeight']
        print(f'\nprevious block convergence matrix is {self.outputMatrix}')