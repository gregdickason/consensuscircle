import json

#utility functions
from agentUtilities import converge, hashvector, getHashofInput, getRandomNumbers, getRandomNumber, getSeed, returnHashDistance, returnCircleDistance, checkBlock  # need to setup as cc utilities


# Parses the last block.  Does not check the chain but will return with either a fully parsed block or with blockPass set to False if the block is not well formed or hashes do not align
class parseBlock:
    def __init__(self):
        with open('FullBlockStructure.json') as json_data:
            self.block = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
        self.blockHash = self.block['blockHash']
        print(f'Block Hash is {self.blockHash}')
        self.blockHeader = self.block['blockHeader']
        self.consensusCircle = self.blockHeader['consensusCircle']
        self.seeds = self.blockHeader['seeds']
        self.matrixHashes = self.blockHeader['blockRandomMatrixHashes']
        self.instructionOpensCount = self.blockHeader['blockInstructionCountOpens']
        self.previousBlock = self.blockHeader['previousBlock']
        self.blockHeight = self.blockHeader['blockHeight']
        self.randomNumbers = self.blockHeader['randomNumbers']  # Need to parse by circle for convergence matrix
        self.randomMatrix = []
        self.consensusCircleMatrix = []
        self.blockPass = True
        self.blockComment = 'Block Conforms'
        
        for e in self.randomNumbers:
          for f in e.values():
            self.randomMatrix.append(f)
        
        for e in self.consensusCircle:
          self.consensusCircleMatrix.append(e['pKey'])

        print(f'randomMatrix is {self.randomMatrix}')
        
        # Now do checks:
        # Is blockhash the same
        # TODO put conditional prints in for debug vs non (logging framework)
        self.calculatedHash = getHashofInput(json.dumps(self.blockHeader))
        print(f'blockhash is: \n{self.blockHash}\nCalculated:\n{self.calculatedHash}\n')
        if self.blockHash != self.calculatedHash:
            self.blockPass = False
            self.blockComment = 'blockHash is not correct'
            return 
        
        # Check hashes and reveals are both correct (so hashed revealed numbers are the hashes produced
        self.matrixHash = []
        self.matrixSeed = []
        
        for e in self.matrixHashes:
            self.matrixHash.append(list(e.values())[0])
        
        for e in self.seeds:
            self.matrixSeed.append(list(e.values())[0])
       
        hlen, slen, rlen, i = len(self.matrixHash), len(self.matrixSeed), len(self.randomMatrix), 0
        if hlen != slen:
          self.blockPass = False
          self.blockComment = 'array length of seeds != array length of blockRandomMatrixHashes'
          return
        
        if rlen != slen:
          self.blockPass = False
          self.blockComment = 'array length of seeds != array length of randomNumbers'
          return
        
        while i < hlen:
          hashInput = getHashofInput(json.dumps(self.randomMatrix[i])+self.matrixSeed[i])
          if hashInput != self.matrixHash[i]:
            self.blockPass = False
            self.blockComment = f'hash of randomNumbers with Seed at {i} is {hashInput} != hashed output in block {self.matrixHash[i]}'
            return
          i += 1
        
        
        # Converge the Matrix
        self.outputMatrix = [g for g in converge(self.randomMatrix ,2**256)]  
        print(f'Converged Matrix is {self.outputMatrix}')
        
        