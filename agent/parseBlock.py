import json
import logging.config

#utility functions
import encryptionUtilities
import blockUtilities
import redisUtilities

# Parses the last block.  Does not check the chain but will return with either a fully parsed block or with blockPass set to False if the block is not well formed or hashes do not align
# Order of execution:
# - Confirm Block is valid JSON, contains the right number of instructions given the header data
# - Confirm blockhash (hash of the header) is correct.  Note header contains the previous block hash
# - Confirm that each member of the consensus circle has signed off the convergenceHeader (signed off merkle roots and random numbers).  This shows convergence
# - Confirm Instructions and InstructionHandlers: number, merkle roots
class parseBlock:
    def __init__(self,blockID, entityInstructions):

        self.block = redisUtilities.getCandidateBlock(blockID)

        logging.debug(f'in parseBlock')
        self.blockHash = self.block['blockHash']
        logging.debug(f'Block Hash is {self.blockHash}')
        self.blockHeader = self.block['blockHeader']
        self.convergenceHeader = self.blockHeader['convergenceHeader']
        self.consensusCircle = self.blockHeader['consensusCircle']
        self.blockSignatures = self.blockHeader['blockSignatures']
        self.instructionCount = self.convergenceHeader['instructionCount']
        self.instructionsMerkleRoot = self.convergenceHeader['instructionsMerkleRoot']
        self.previousBlock = self.convergenceHeader['previousBlock']
        self.blockHeight = self.convergenceHeader['blockHeight']
        self.randomNumbers = self.convergenceHeader['randomNumbers']  # Need to parse by circle for convergence matrix
        self.instructions = self.block['instructions']

        self.randomMatrix = []
        self.ccKeys = []
        self.blockSigs = []

        self.instructionHashes = []
        self.instructionBodies = []

        self.blockPass = True
        self.blockComment = 'Block Conforms'

        logging.debug(f'checking block not on chain {self.blockHash}')
        if (redisUtilities.blockExists(self.blockHash)):
            self.blockPass = False
            self.blockComment = "this block is already on the chain"

        logging.debug(f'checking previous block {self.previousBlock} exists')
        if not (redisUtilities.blockExists(self.previousBlock)):
            self.blockPass = False
            self.blockComment = "previous block is not known to this agent"

        logging.debug(f'checking the block height is correct relative to the identified previous block')
        if (self.blockHeight != (redisUtilities.getBlockHeight(self.previousBlock)+1)):
            self.blockPass = False
            self.blockComment = "block height incorrect"
            logging.info(f'block height is not valid. was: {self.blockHeight}, should be: {redisUtilities.getBlockHeight()+1}')

        logging.debug(f'random Numbers are {self.randomNumbers}')
        for e in self.randomNumbers:
          for f in e.values():
            self.randomMatrix.append(f)

        for e in self.consensusCircle:
          self.ccKeys.append(e['agentID'])

        logging.info(f'randomMatrix is {self.randomMatrix}')

        # Now do checks:
        # Is blockhash the same
        # TODO confirm json.dumps is deterministic.  If order changes then hash will change.  May need more reliable approach
        # TODO use orderedDict for loading: https://stackoverflow.com/questions/2774361/json-output-sorting-in-python
        self.calculatedHash = encryptionUtilities.getHashofInput(self.blockHeader)
        logging.info(f'blockhash is: \n{self.blockHash}\nCalculated:\n{self.calculatedHash}\n')
        if self.blockHash != self.calculatedHash:
            self.blockPass = False
            self.blockComment = 'blockHash is not correct'
            return

        # Are the instructions hashed and signed?
        for e in self.instructions:
          validInstruction = blockUtilities.validateInstruction(e)
          if not validInstruction['return']:
            self.blockPass = False
            self.blockComment = validInstruction['message']
            return
          self.instructionHashes.append(e['instructionHash'])

        # Check instruction count is the same from header
        if self.instructionCount != len(self.instructionHashes):
          self.blockPass = False
          self.blockComment = f'instructionCount is not same as number instructions'
          return

        # Does the merkleroot of the instructions map to the header?
        if encryptionUtilities.returnMerkleRoot(self.instructionHashes) != self.instructionsMerkleRoot:
          self.blockPass = False
          logging.info(f'merkle root does not match got {encryptionUtilities.returnMerkleRoot(self.instructionHashes)} expected {self.instructionsMerkleRoot}')
          self.blockComment = f'instruction merkle root of {self.instructionsMerkleRoot} != calculated merkle root of {encryptionUtilities.returnMerkleRoot(self.instructionHashes)}'
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

        hashConvergenceHeader = encryptionUtilities.getHashofInput(self.convergenceHeader)
        logging.info(f'\nhash of convergenceHeader is {hashConvergenceHeader}\n')
        while i < clen:
          if encryptionUtilities.verifyMessage(hashConvergenceHeader,self.blockSigs[i], redisUtilities.getPublicKey(self.ccKeys[i])) != True:
            self.blockPass = False
            self.blockComment = f'signature for Circle at {i} is not valid'
            return
          i += 1

        # Converge the Matrix
        self.outputMatrix = [g for g in encryptionUtilities.converge(self.randomMatrix ,2**256)]
        logging.info(f'Converged Matrix is {self.outputMatrix}')

        self.circleDistance = encryptionUtilities.returnCircleDistance(redisUtilities.getOutputMatrix(self.previousBlock), self.ccKeys, self.instructionCount, entityInstructions)

        # remove anything that there is duplicates of for printing
        del self.block
        del self.convergenceHeader
        del self.consensusCircle
        del self.blockSignatures
        del self.instructionCount
        del self.instructionsMerkleRoot
        del self.previousBlock
        del self.blockHeight
        del self.randomNumbers
        del self.randomMatrix

        return

    def getOutputMatrix(self):
        return self.outputMatrix

    def getBlockHash(self):
        return self.blockHash

    def getPreviousBlock(self):
        return self.blockHeader['convergenceHeader']['previousBlock']

    def getCircleDistance(self):
        return self.circleDistance

    def getBlockHeight(self):
        return self.blockHeader['convergenceHeader']['blockHeight']

    def getInstructions(self):
        return self.instructions

    def getBlockPass(self):
        return self.blockPass

    def getBlockComment(self):
        return self.blockComment

    def getOutputMatrix(self):
        return self.outputMatrix
