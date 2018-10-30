import json
import logging.config

from blockState import blockState 

#utility functions
from agentUtilities import converge, hashvector, getHashofInput, getRandomNumbers, getRandomNumber, getSeed, returnHashDistance, verifyMessage, returnMerkleRoot 
from processInstruction import validateInstruction, validateInstructionHandler

# Parses the last block.  Does not check the chain but will return with either a fully parsed block or with blockPass set to False if the block is not well formed or hashes do not align
# Order of execution:
# - Confirm Block is valid JSON, contains the right number of instructions given the header data
# - Confirm blockhash (hash of the header) is correct.  Note header contains the previous block hash
# - Confirm that each member of the consensus circle has signed off the convergenceHeader (signed off merkle roots and random numbers).  This shows convergence
# - Confirm Instructions and InstructionHandlers: number, merkle roots
class parseBlock:
    def __init__(self,blockID):
        with open(blockID) as json_data:
            self.block = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
        
        logging.debug(f'in parseBlock')
        self.blockHash = self.block['blockHash']
        logging.debug(f'Block Hash is {self.blockHash}')
        self.blockHeader = self.block['blockHeader']
        self.convergenceHeader = self.blockHeader['convergenceHeader']
        self.consensusCircle = self.blockHeader['consensusCircle']
        self.blockSignatures = self.blockHeader['blockSignatures']
        self.instructionCount = self.convergenceHeader['instructionCount']
        self.instructionHandlerCount = self.convergenceHeader['instructionHandlerCount']
        self.instructionsMerkleRoot = self.convergenceHeader['instructionsMerkleRoot']
        self.instructionHandlersMerkleRoot = self.convergenceHeader['instructionHandlersMerkleRoot']
        self.previousBlock = self.convergenceHeader['previousBlock']
        self.blockHeight = self.convergenceHeader['blockHeight']
        self.randomNumbers = self.convergenceHeader['randomNumbers']  # Need to parse by circle for convergence matrix
        self.instructions = self.block['instructions']
        self.instructionHandlers = self.block['instructionHandlers']
        
        self.circleDistance = 0    # This is set externally when the distance is calculated
      
        self.randomMatrix = []
        self.ccKeys = []
        self.blockSigs = []
        
        self.instructionHashes = []
        self.instructionHandlerHashes = []
        self.instructionBodies = []
      
        self.blockPass = True
        self.blockComment = 'Block Conforms'
        
        # TODO - should we be getting the blockState instance from the agent not creating our own instance?
        self.bState = blockState()
        logging.debug(f'random Numbers are {self.randomNumbers}')
        for e in self.randomNumbers:
          for f in e.values():
            self.randomMatrix.append(f)
        
        for e in self.consensusCircle:
          self.ccKeys.append(e['pKey'])

        logging.info(f'randomMatrix is {self.randomMatrix}')
        
        # Now do checks:
        # Is blockhash the same
        # TODO confirm json.dumps is deterministic.  If order changes then hash will change.  May need more reliable approach
        # TODO use orderedDict for loading: https://stackoverflow.com/questions/2774361/json-output-sorting-in-python
        self.calculatedHash = getHashofInput(json.dumps(self.blockHeader))
        logging.info(f'blockhash is: \n{self.blockHash}\nCalculated:\n{self.calculatedHash}\n')
        if self.blockHash != self.calculatedHash:
            self.blockPass = False
            self.blockComment = 'blockHash is not correct'
            return 
        
        # Are the instructions hashed and signed? 
        # TODO in agent code: these can already be verified so maybe here we simply check that we have already processed transaction rather than reprocess?
        # TODO in agent code - remove them from the pool IF THE BLOCK PASSES
        for e in self.instructions:
          validInstruction = validateInstruction(e,self.bState)
          if not validInstruction['return']:
            self.blockPass = False
            self.blockComment = validInstruction['message']
            return
          # TODO Check signatures - if verifyMessage( .... )   
          self.instructionHashes.append(e['instructionHash'])
          
        # Check instruction count is the same from header
        if self.instructionCount != len(self.instructionHashes):
          self.blockPass = False
          self.blockComment = f'instructionCount is not same as number instructions'
          return
                  
        
        # Does the merkleroot of the instructions map to the header?
        if returnMerkleRoot(self.instructionHashes) != self.instructionsMerkleRoot:
          self.blockPass = False
          self.blockComment = f'instruction merkle root of {self.instructionsMerkleRoot} != calculated merkle root of {returnMerkleRoot(self.instructionHashes)}'
          return
          
        # Are the instructionHandlers hashed and signed? 
        # TODO in agent code: these can already be verified so maybe here we simply check that we have already processed rather than reprocess?
        # TODO in agent code - remove them from the pool IF THE BLOCK PASSES
        for e in self.instructionHandlers:
          validInstructionHandler = validateInstructionHandler(e)          
          if not validInstructionHandler['return']:
            self.blockPass = False
            self.blockComment = validInstructionHandler['message']
            return
          # TODO Check signatures - if verifyMessage( .... )   
          self.instructionHandlerHashes.append(e['instructionHandlerHash'])
          
        # Check instruction count is the same from header
        if self.instructionHandlerCount != len(self.instructionHandlerHashes):
          self.blockPass = False
          self.blockComment = f'instructionHandlerCount is not same as number instructionHandlers'
          return
                  
        
        # Does the merkleroot of the instructionHandlers map to the header?
        if returnMerkleRoot(self.instructionHandlerHashes) != self.instructionHandlersMerkleRoot:
          self.blockPass = False
          self.blockComment = f'instructionHandler merkle root of {self.instructionHandlersMerkleRoot} != calculated merkle root of {returnMerkleRoot(self.instructionHandlerHashes)}'
          return
        
        
        # Check consensus circle has signed off on the convergenceHeader
        logging.debug(f'parsing  blockSig {self.blockSignatures}')
        for e in self.blockSignatures:        
            self.blockSigs.append(list(e.values())[0])
       
        rlen, clen, blen, j, i = len(self.randomMatrix),len(self.ccKeys),len(self.blockSigs), 0, 0
        
        # Check Lengths
        if rlen != clen:
          selfblockPass = False
          self.blockComment = 'array length of random Numbers not same as consensusCircle'
          return
        
        if blen != clen:
          selfblockPass = False
          self.blockComment = 'length of block Signatures not same as consensusCircle'
          return
	
        hashConvergenceHeader = getHashofInput(json.dumps(self.convergenceHeader))
        logging.info(f'\nhash of convergenceHeader is {hashConvergenceHeader}\n')
        while i < clen:
          if verifyMessage(hashConvergenceHeader,self.blockSigs[i], self.bState.getPubKey(self.ccKeys[i])) != True:
            self.blockPass = False
            self.blockComment = f'signature for Circle at {i} is not valid'
            return
          i += 1  
        
        # check merkle roots etc - if we fail here there is a major issue as the whole circle has signed off.
        # TODO
        
        
        # Converge the Matrix
        self.outputMatrix = [g for g in converge(self.randomMatrix ,2**256)]  
        logging.info(f'Converged Matrix is {self.outputMatrix}')
        
        return