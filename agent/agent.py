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
from parseBlock import parseBlock
import blockUtilities
import redisUtilities
from trackedAgent import trackedAgent  #TODO do we need this?
from globalsettings import AgentSettings

#utility functions - add to class?
from agentUtilities import getHashofInput, converge, hashvector, returnMerkleRoot,getRandomNumbers, getRandomNumber, getSeed, returnHashDistance, returnCircleDistance, verifyMessage, signMessage
from processInstruction import validateInstruction

class Agent:
    def __init__(self):
        # TODO load from blockstate?  (handles long term state)
        #self.current_instructions = [] # Pool of unprocessed instructions we are aware of, sent from other agents (do through non http protocol?)
        settings = AgentSettings()

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
        logging.debug(f'setting agent identifier to {settings.agentIdentifier}')
        self.agent_identifier = settings.agentIdentifier
        self.owner = settings.ownerID  # TODO confirm that the owner has signed the public key of the agent - have to lookup the key
        self.signedIdentifier = settings.signedIdentifier
        self.agentPrivateKey = settings.agentPrivateKey

    def changeConfig(self,ownerLevel, agentIdentifier, ownerID, signId, agentPrivateKey):
        agentResponse = {}
        self.level = ownerLevel # TODO should come from the agents owner's level
        self.agent_identifier = agentIdentifier
        self.owner = ownerID      # TODO confirm that the owner has signed the public key of the agent - have to lookup the key
        self.signedIdentifier = signId
        self.agentPrivateKey = agentPrivateKey  #TODO - do we want to accept private key updates?  (will be over SSL)

        agentResponse['message'] = {
           'message': f'Updated agent config'
          }
        agentResponse['success'] = True

        return agentResponse

    def getLastBlock(self):
        return {
            'lastBlock': redisUtilities.getBlockHash(),
            'blockHeight': redisUtilities.getBlockHeight(),
            'circleDistance': redisUtilities.getCircleDistance()
        }

    def getOwner(self):
        return self.owner

    def getLevel(self):
        return self.level

    def getPrivateKey(self):
        return self.agentPrivateKey

    def setPrivateKey(self, privateKey):
        self.agentPrivateKey = privateKey
        return

    def getConfig(self):
        agentConfig = {}
        agentConfig['level'] = self.level
        agentConfig['agentIdentifier'] = self.agent_identifier
        agentConfig['owner'] = self.owner
        agentConfig['signedIdentifier'] = self.signedIdentifier
        agentConfig['agentPrivateKey'] = self.agentPrivateKey

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

    def getEntityList(self):
        return redisUtilities.getEntityList()

    # returns the list of attributes the entity has.  Hardcoded to test
    def getAttributes(self):
        return ['wallets.default.balance']

    # Routine to get the current instruction pool we dont test convergence, any following agent can get this to populate their pool
    def instructionPool(self):
        logging.debug(f'In instructionPool')
        agentResponse = {}

        # TODO - get this from the blockstate

        # Need to get the merkle root from the instruction pool. - I
        instruction_hashes = redisUtilities.getInstructionHashes()
        hashMerkle = returnMerkleRoot(instruction_hashes)
        hashSigned = signMessage(hashMerkle,self.agentPrivateKey)
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
        newBlock = parseBlock(blockID, self.entityInstructions)

        # is the block Valid?
        if newBlock.getBlockPass() == False:
            agentResponse['message'] = {
                     'chainLength' : redisUtilities.getBlockHeight(),
                     'lastBlock': redisUtilities.getBlockHash(),
                      'error': newBlock.getBlockComment()
             }
            agentResponse['success'] = False
            return agentResponse

        # forking - if forks can be of depth > 1 before agent seeing a block in the fork
        # then parse block will need to be updated
        if (redisUtilities.getNextBlock(newBlock.getPreviousBlock()) != None): #there is some kind of fork
            logging.debug('A FORK HAS BEEN DISCOVERED!')
            if (redisUtilities.getNextBlock(newBlock.getPreviousBlock()) == redisUtilities.getBlockHash()):
                # circle distance is calculated in parseBlock relative to the named previous block
                # so all you need to do is retrieve and compare the circle distance value
                # for the two competing blocks
                if (redisUtilities.getCircleDistance() <= int(newBlock.getCircleDistance(),16)):
                    agentResponse['message'] = {
                             'chainLength' : redisUtilities.getBlockHeight(),
                             'lastBlock': redisUtilities.getBlockHash(),
                              'error': 'newBlock was a fork on current block and current block had a smaller circle distance'
                     }
                    agentResponse['success'] = False
                    return agentResponse
                else:
                    blockUtilities.rollBack(newBlock.getPreviousBlock())
            else:
                #get weighted circle distance and compare. potentially rule out
                heightDiff = redisUtilities.getHeightDiff(newBlock.getPreviousBlock)
                newBlockWeightedCircleDistance = newBlock.getCircleDistance() + newBlock.getCircleDistance() * (heightDiff - 1)
                if (redisUtilities.getWeightedCircleDistance(newBlock.getPreviousBlock()) < newBlockWeightedCircleDistance):
                    agentResponse['message'] = {
                             'chainLength' : redisUtilities.getBlockHeight(),
                             'lastBlock': redisUtilities.getBlockHash(),
                              'error': 'newBlock was a fork on current block and current chain had a smaller weighted circle distance'
                     }
                    agentResponse['success'] = False
                else:
                    blockUtilities.rollBack(newBlock.getPreviousBlock())

        # Normal processing, new block built on our chain.  READ NOTES
        # execute instructions on the block state and update the block state to the latest
        blockUtilities.addNewBlock(newBlock)

        logging.info(f'\n ** NEW BLOCK PUBLISHED. ** Block distance = {newBlock.getCircleDistance()}\n')

        # TODO: next circle could have race condition for a promoted agent.  Agents need some N number of blocks old before being eligible (to stop race condition)
        logging.debug(f'New block output matrix is {newBlock.getOutputMatrix()}')

        # move to RQ Worker
        # blockUtilities.generateNextCircle()

        # logging.info(f'\nNext circle is {self.nextCircle}\n')

        agentResponse['message'] = {
            'chainLength' : newBlock.getBlockHeight(),
            'lastBlock': newBlock.getBlockHash(),
            'circleDistance': newBlock.getBlockComment()
        }
        return agentResponse

    #execute instruction
    def executeInstruction(self, instruction):
        #call blockstate to execute instruction

        return blockUtilities.executeInstruction(instruction)


    def processInstruction(self, instruction):
        agentResponse = {}

        # check hash
        validInstruction = validateInstruction(instruction)
        if not validInstruction['return']:
            logging.debug(f'Instruction not valid: {instruction}')
            agentResponse['success'] = False
            agentResponse['message'] = validInstruction['message']
            return agentResponse

        #check if the instruction is already in the pool
        if redisUtilities.hasInstruction(instruction['instructionHash']):
            logging.info(f'Received instruction already have')
            agentResponse['success'] = False
            agentResponse['message'] = 'Instruction already in pool'
            return agentResponse

        # if not already in the pool add to the block state
        blockUtilities.addInstruction(instruction)

        agentResponse['message'] = "Instruction added"
        agentResponse['success'] = True

        return agentResponse

    def getEntity(self, entity):
        # gets entity as a JSON object referenced by the public key.
        # TODO Error handling or return 'Entity not found JSON object'
        agentResponse = {}
        agentResponse['success'] = True
        agentResponse['message'] = redisUtilities.getEntity(entity)
        if agentResponse['message'] == '':
          agentResponse['success'] = False

        return agentResponse

    def getAttribute(self, entity, attribute):
        # gets an attribute.  This can include the balance of a wallet, or the setting for a particular attribute.
        # if the attribute does not exist returns null
        agentResponse = {}
        agentResponse['success'] = True
        agentResponse['message'] = redisUtilities.getAttribute(entity, attribute)
        if agentResponse['message'] == '':
          agentResponse['success'] = False

        return agentResponse

    def getGenesisHash(self):
        return redisUtilities.getGenesisHash()

# TODO Put this in a separate module with class that loads up from persistent storage?
    def postCandidateStructure(self):
     # Setup the candidate structure and post to our convergenceProcessor to kick off the convergence process
     candidate = {}
     candidate["gossip"] = []

     # TODO Use an orderedMap here for consistent Hash
     # myMap = {}
     # myMap["previousBlock"] = self.blockState.getBlockHash()
     # myMap["instructionsMerkleRoot"] = returnMerkleRoot(self.blockState.getInstructionHashes())
     # myMap["instructionCount"] = len(self.blockState.getInstructionList())
     # # TODO update instructionHandlers
     # # TODO fix as chain 0 isnt highest block?  Append issue?
     # myMap["blockHeight"] = (self.blockState.getBlockHeight() + 1) # 1 higher for next block
     # myMap["randomNumberHash"] = [g for g in hashvector(self.randomMatrix, self.seed)]
     # myGossip = {}
     # myGossip[self.agent_identifier] = myMap
     # myGossip["sign"] = signMessage(myMap, self.agentPrivateKey)
     # myGossip["trusted"] = 1   # I trust myself
     # candidate["gossip"].append(myGossip)
     # candidate["broadcaster"] = self.agent_identifier
     # candidate["signedGossip"] = signMessage(myGossip, self.agentPrivateKey)
     # candidate["instructionHashes"] = list(self.blockState.getInstructionHashes())
     # candidate["instructions"] = list(self.blockState.getInstructionList())

     # we send randomMatrix and seed too so this can be reused
     mySettings = {}
     mySettings["randomMatrix"] = list(self.randomMatrix)
     mySettings["seed"] = self.seed
     candidate["agentSettings"] = mySettings

     # post structure - do this through blockState
     blockUtilities.postJob(candidate)
     logging.debug(f'candidate = {candidate}')


     return
