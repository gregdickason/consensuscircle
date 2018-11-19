#!/usr/bin/python

import hashlib
import json
from time import time
from urllib.parse import urlparse
import urllib.request
from uuid import uuid4
import threading

import logging.config

import collections
import copy

# classes managing the aspects of the blockchain an agent needs in this simulation: the lastBlock, the agents they are following for updates.
from lastBlock import lastBlock
from parseBlock import parseBlock
from genesisBlock import genesisBlock
from blockState import blockState
from trackedAgent import trackedAgent  #TODO do we need this?
from globalsettings import AgentSettings

#utility functions - add to class?
from agentUtilities import getHashofInput, converge, hashvector, returnMerkleRoot,getRandomNumbers, getRandomNumber, getSeed, returnHashDistance, returnCircleDistance, verifyMessage, signMessage
from processInstruction import validateInstruction, validateInstructionHandler

class Agent:
    def __init__(self):
        # TODO load from blockstate?  (handles long term state)
        #self.current_instructions = [] # Pool of unprocessed instructions we are aware of, sent from other agents (do through non http protocol?)
        settings = AgentSettings()

        self.chain = collections.deque(maxlen = 100) # TODO make part of blockState (local means in redis)
        self.entityInstructions = settings.entityInstructions
        self.followedAgents = set()   #  set of agents we follow for updates when operating in the circle.
        self.trackedCircleAgents = {}  # dictionary(map) that this agent uses to converge: checking the outputs from other agents to allow gossip checks and for the convergence protocol to determine the next circle
        self.nextCircle , self.randomMatrix, self.randomMatrixHash = [], [], []
        self.seed = 0

        # this is the level of the agent.  Starts at 5 which is ineligible for circle membership
        self.inCircle = False  # we are not in a circle by default

        # TODO: Remove, we track based on the config in blockState
        self.maxAgentsInCircle = settings.maxAgentsInCircle  # set to 1 below number as we are a member of the circle when this is tested

        # setup my randomNumbers, my hashed random numbers, and seed for my vote for the next chain.
        self.randomMatrix = [g for g in getRandomNumbers(2,5)]
        self.seed = getSeed(2)
        self.randomMatrixHash = [g for g in hashvector(self.randomMatrix, self.seed)]
        # only logged in debug mode to avoid outside chance of leaking secrets
        logging.debug(f'Agents random matrix, seed and hash is {self.randomMatrix}, {self.seed}, {self.randomMatrixHash}')

        # TODO put these as loaded from blockstate
        # We have default settings we load on startup that get overridden by the appropriate setup call if signed correctly (
        self.level = settings.level   # TODO this should be confirmed by the agent from the owners level (not independent).  In the blockState object
        self.agent_identifier = settings.agentIdentifier
        self.owner = settings.ownerPKey  # TODO confirm that the owner has signed the public key of the agent - have to lookup the key
        self.signedIdentifier = settings.signedIdentifier
        self.agentPrivKey = settings.agentPrivateKey

        logging.debug('Getting blockchain State')
        self.blockState = blockState()
        logging.debug('Parsing Genesis Block')
        self.genesisBlock = genesisBlock()

        # add genesis block to the chain on startup if we have no state we can read from
        if self.blockState.blockHeight == 0:
            self.chain.append(self.genesisBlock)
        # TODO elif we already have state then we need to get other blocks from agents to see if we are up to date

        # update config when we get setup - needs the owner to sign off to allow change
        # TODO Confirm that the owner of the agent has signed off changes or dont change

    def changeConfig(self,ownerLevel, agentIdentifier, ownerPKey, signId, agentPrivKey):
        agentResponse = {}
        self.level = ownerLevel # TODO should come from the agents owner's level
        self.agent_identifier = agentIdentifier
        self.owner = ownerPKey      # TODO confirm that the owner has signed the public key of the agent - have to lookup the key
        self.signedIdentifier = signId
        self.agentPrivKey = agentPrivKey  #TODO - do we want to accept private key updates?  (will be over SSL)

        agentResponse['message'] = {
           'message': f'Updated agent config'
          }
        agentResponse['success'] = True

        return agentResponse


    def getConfig(self):
        agentConfig = {}
        agentConfig['level'] = self.level
        agentConfig['agentIdentifier'] = self.agent_identifier
        agentConfig['owner'] = self.owner
        agentConfig['signedIdentifier'] = self.signedIdentifier
        agentConfig['agentPrivateKey'] = self.agentPrivKey

        return agentConfig

        # Register an agent to follow.  This is our direct connections to other agents in the circle.  #TODO should be from the knownAgents.json config and using helper classes as this will be not always HTTP
    def register_agent(self, address):
        """
        Add a new agent to the list of agents we are following for instructions.  For now we dont check if they are valid
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)

        if parsed_url.netloc:
            self.followedAgents.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.followedAgents.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')



    def add_instructionHandler(self, hash, instructionHandler, sign):

        # Check hash is right - if not error (TODO: block the calling agent)
        # Also check if we trust the sender.  If not then block.  TODO - create trusted senders list we share with others
        if getHashofInput(instructionHandler) != hash:
            return 0

        # check if the hash has already been received for this instruction and if so then dont append
        # TODO get from blockstate if in the pool
        if hash in self.instruction_Handlerhashes:
            logging.info(f'Received instructionHandler already have, instructionHandler hashes are {self.instruction_Handlerhashes}')
            return len(self.blockState.current_Handlerinstructions)

        # This is Mutexed for hash control
        # TODO add to the redis pool in the blockstate
        # TODO Separate InstructionHandler mutex?  or no mutex?

        self.blockState.addInstructionHandler(instructionHandler,hash,sign)
        # TODO get from blockstate if in pool (not from our hash list)
        self.instruction_Handlerhashes.add(hash)
        logging.debug(f'instructionHandler hashes are {self.instruction_Handlerhashes}')
        # TODO - get the length from the blockstate
        return len(self.instruction_Handlerhashes)


    # Routine to get the current instruction pool we dont test convergence, any following agent can get this to populate their pool
    def instructionPool(self):
        logging.debug(f'In instructionPool')
        agentResponse = {}

        # TODO - get this from the blockstate

        # Need to get the merkle root from the instruction pool. - I
        instruction_hashes = self.blockState.getInstructionHashes()
        hashMerkle = returnMerkleRoot(instruction_hashes)
        hashSigned = signMessage(hashMerkle,self.agentPrivKey)
        agentResponse['message'] = {
                 'merkleRoot': hashMerkle,
                 'signed':hashSigned,
                 'hashes':list(instruction_hashes)
               }
        agentResponse['success'] = True
        return agentResponse


    def processBlock(self, blockID):
        # Testing parameters - is network on
        agentResponse = {}
        agentResponse['success'] = True

        logging.debug("new block published, retrieve validate and process it")
        # TODO - make parseBlock take the argument of the hash on top of the chain.  If same return immediately to reduce time spent in parseBlock
        newBlock = parseBlock(blockID)


        # is the block Valid?
        if newBlock.blockPass == False:
            agentResponse['message'] = {
                     'chainLength' : len(self.chain) - 1,
                     'lastBlock': self.chain[len(self.chain)-1].blockHash,
                      'error': newBlock.blockComment
             }
            agentResponse['success'] = False
            return agentResponse

        # if this is the same blockHeight we have already processed - check if circle distance is closer (i.e. there is more random outputs and therefore more
        # coinbase transactions to recognise, plus we need to reprocess who should be in the circle)
        # TODO - Circle Distance Check, Look at even lower in the stack as lower height still forkable
        if newBlock.blockHeight == self.chain[len(self.chain)-1].blockHeight:
            logging.debug(f'Block published - same height as previous block.  Ignore for now')
            agentResponse['message'] = {
                'chainLength' : len(self.chain) - 1,
                'lastBlock': self.chain[len(self.chain)-1].blockHash,
                'circleDistance': self.chain[len(self.chain)-1].circleDistance
            }
            return agentResponse
        elif newBlock.previousBlock != self.chain[len(self.chain)-1].blockHash:
            # This is not building on the top of our chain.  Need to work out if in the chain and deeper down, a fork or are we missing a block.  Do we need to sync
            # TODO If not then calculate the circleDistance and if lower then use this block (accept the fork)  --> which means undoing instructions that have completed
            # TODO on this (look at blockheight, etc).  Also need to make sure we cant be attacked with something random that consumes processing power
            # if lower down we need to reprocess the coinbase transactions
            logging.debug(f'Block published - not referencing previous block hash')
            agentResponse['message'] = {
                   'message' : 'Received block not in chain.  need to manage it TODO'
                  }
            return agentResponse

        # Normal processing, new block built on our chain.  READ NOTES

        # Newblock circle distance needs to be calculated off the old block outputMatrix
        newBlock.circleDistance = returnCircleDistance(newBlock.ccKeys, self.chain[len(self.chain)-1].outputMatrix, newBlock.instructionCount,self.entityInstructions)
        logging.info(f'\n ** NEW BLOCK PUBLISHED. ** Block distance = {newBlock.circleDistance}\n')

        # TODO confirm that the block is shortest distance
        self.chain.append(newBlock)


        # TODO process instructions and remove from unprocessed pool if in the block  (TODO work out how to roll back if a new block is better)

        # TODO: next circle could have race condition for a promoted agent.  Agents need some N number of blocks old before being eligible (to stop race condition)
        logging.debug(f'New block output matrix is {newBlock.outputMatrix}')
        self.nextCircle = self.blockState.nextCircle(newBlock.outputMatrix, [])  # No excluded agents for now

        # TODO: check if already in a circle and what this block means - do we stop processing?

        # Am I in the circle?
        # TODO - check if in potentially a secondary circle.  If so start the convergence using this one in case primary fails
        if self.agent_identifier in self.nextCircle:
          self.inCircle = True

          # Re-randomise the random hash we will use to converge (for each initiation of a block we are in):
          self.randomMatrix = [g for g in getRandomNumbers(32,5)]  # TODO - based on number in circle so need to use this parameter
          self.seed = getSeed(32)
          logging.info(f'\n** Agent is in next Circle**\n')
          # TODO setup candidate data structure and send to convergenceProcessor
          self.postCandidateStructure()


        logging.info(f'\nNext circle is {self.nextCircle}\n')

        agentResponse['message'] = {
            'chainLength' : len(self.chain) - 1,
            'lastBlock': self.chain[len(self.chain)-1].blockHash,
            'circleDistance': newBlock.circleDistance
        }
        return agentResponse

    # TODO: setup instruction handling and instructions.  2 sides to allow data management.
    # For example, and offer from a company will be an instrcution handler: 'if you have these attributes and you send me this proof through an instruction, this handler will do XYZ'
    # The above allows people to 'always opt in' through delegating agents to share some of their data (with shared keys), to opt in when they want, to partiipate in anonymous surveys (through anonymous matching of their attributes), to contribute and earn from models,or to never opt in but understand the value of the data they have
    def processInstruction(self,instruction):
        # Add an instruction to the pool of unprocessed instructions
        logging.debug('received an instruction to add')
        agentResponse = {}
        agentResponse['success'] = True
        agentResponse['message'] = ''

        # Check that the required fields are in the POST'ed data, has been signed correctly, etc
        validInstruction = validateInstruction(instruction, self.blockState)
        if not validInstruction['return']:
          logging.debug(f'Instruction not valid: {instruction}')
          agentResponse['success'] = False
          agentResponse['message'] = validInstruction['message']
          return agentResponse

        # check if the hash has already been received for this instruction and if so then dont append
        # checks both in our existing hashpool and in previous blocks
        if self.blockState.hasInstruction(instruction['instructionHash']):
            logging.info(f'Received instruction already have')
            agentResponse['message'] = 'Instruction already in pool'
            # dont return length of pool - no need
            return agentResponse

        # This is Mutexed for hash control
        # TODO add to the redis pool in the blockstate - done in blockState.addInstruction

        # TODO - update the entities too - load these GREG HERE
        self.blockState.addInstruction(instruction['instruction'],instruction['instructionHash'],instruction['sign'])
        # TODO get from blockstate if in pool (not from our hash list)
        #self.instruction_hashes.add(hash)

        # TODO - get the length from the blockstate

        agentResponse['message'] = {
            'message': f'Instruction added'
        }
        return agentResponse

    def processInstructionHandler(self,values):
        # Add an instructionHandler to the pool of unprocessed instructionHandlers
        logging.debug("received an instructionHandler to add")
        agentResponse = {}
        agentResponse['success'] = True
        agentResponse['message'] = ''
        # Check that the required fields are in the POST'ed data
        validInstructionHandler = validateInstructionHandler(values)

        if not validInstructionHandler['return']:
          return validInstructionHandler

        # TODO: put into Blockstate here
        #GREG HERE fix redis and then can check agent working
        numberInstructionHandlers = self.add_instructionHandler(values['instructionHandlerHash'], values['instructionHandler'], values['sign'])

        agentResponse['message'] = {
            'message': f'Agent currently has {numberInstructionHandlers} instructionHandlers in the unprocessed pool',
            'instructionHandlers': list(self.instruction_Handlerhashes)
        }
        return agentResponse


    def getEntity(self, entity):
        # gets entity as a JSON object referenced by the public key.
        # TODO Error handling or return 'Entity not found JSON object'
        agentResponse = {}
        agentResponse['success'] = True
        agentResponse['message'] = self.blockState.getEntity(entity)
        if agentResponse['message'] == '':
          agentResponse['success'] = False


        return agentResponse




# TODO Put this in a separate module with class that loads up from persistent storage?
    def postCandidateStructure(self):
     # Setup the candidate structure and post to our convergenceProcessor to kick off the convergence process
     candidate = {}
     candidate["gossip"] = []

     # TODO Use an orderedMap here for consistent Hash
     myMap = {}
     myMap["previousBlock"] = self.chain[len(self.chain)-1].blockHash
     myMap["instructionsMerkleRoot"] = returnMerkleRoot(self.blockState.getInstructionHashes())
     myMap["instructionHandlersMerkleRoot"] = returnMerkleRoot(self.blockState.current_instructionHandlers)  # TODO - make sure instructionHandlers managed same as instructions in Redis.  Fix this
     myMap["instructionCount"] = len(self.blockState.current_instructions)
     # TODO update instructionHandlers
     myMap["instructionHandlerCount"] = len(self.blockState.current_instructionHandlers)
     # TODO fix as chain 0 isnt highest block?  Append issue?
     myMap["blockHeight"] = self.chain[len(self.chain)-1].blockHeight + 1 # 1 higher for next block
     myMap["randomNumberHash"] = [g for g in hashvector(self.randomMatrix, self.seed)]
     myGossip = {}
     myGossip[self.agent_identifier] = myMap
     myGossip["sign"] = signMessage(myMap, self.agentPrivKey)
     myGossip["trusted"] = 1   # I trust myself
     candidate["gossip"].append(myGossip)
     candidate["broadcaster"] = self.agent_identifier
     candidate["signedGossip"] = signMessage(myGossip, self.agentPrivKey)
     candidate["instructionHashes"] = list(self.blockState.getInstructionHashes())
     candidate["instructions"] = list(self.blockState.getInstructionList())
     candidate["instructionHandlerHashes"] = list(self.blockState.getInstructionHashes())
     candidate["instructionHandlers"] = list(self.blockState.getInstructionHandlerList())

     # we send randomMatrix and seed too so this can be reused
     mySettings = {}
     mySettings["randomMatrix"] = list(self.randomMatrix)
     mySettings["seed"] = self.seed
     candidate["agentSettings"] = mySettings

     # post structure - do this through blockState
     self.blockState.postJob(candidate)
     logging.debug(f'candidate = {candidate}')


     return
