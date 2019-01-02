#!/usr/bin/python

import hashlib
import json
from time import time
from urllib.parse import urlparse
import urllib.request
from uuid import uuid4
import threading

import logging.config
import ccExceptions
import collections
import copy

# classes managing the aspects of the blockchain an agent needs in this simulation: the lastBlock, the agents they are following for updates.
from parseBlock import parseBlock
import blockUtilities
import redisUtilities
from trackedAgent import trackedAgent  #TODO do we need this?
from globalsettings import AgentSettings

#utility functions - add to class?
import encryptionUtilities

class Agent:
    # initialise agent by connecting to the data base and claiming the agent id so that
    # the agent knows the rests of its settings
    def __init__(self):
        settings = AgentSettings()

        self.maxAgentsInCircle = settings.maxAgentsInCircle  # set to 1 below number as we are a member of the circle when this is tested
        self.entityInstructions = settings.entityInstructions
        self.followedAgents = set()   #  set of agents we follow for updates when operating in the circle.
        self.seed = 0

        # setup my randomNumbers, my hashed random numbers, and seed for my vote for the next chain.
        self.agentID = "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675"
        redisUtilities.setMyID(self.agentID)
        self.agentPrivateKey = "f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e"

    # Part 1: actions unique to the agent (the majority of its work)

    # process block, veirfy and then add the block with block ID to the chain
    # start the process of creating a new candidate block for the next circle
    # to vote on
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
        try:
          blockUtilities.addNewBlock(newBlock)
        except BlockError as bError:
          logging.error(f'Block parsing failed - error {bError.reason} for block id {bError.id}')
          agentResponse['message'] = {
                   'chainLength' : redisUtilities.getBlockHeight(),
                   'lastBlock': redisUtilities.getBlockHash(),
                   'error': f'block failed to process - {bError.reason}'
                     }
          agentResponse['success'] = False
          return agentResponse

        logging.info(f'\n ** NEW BLOCK PUBLISHED. ** Block distance = {newBlock.getCircleDistance()}\n')

        # TODO: next circle could have race condition for a promoted agent.  Agents need some N number of blocks old before being eligible (to stop race condition)
        logging.debug(f'New block output matrix is {newBlock.getOutputMatrix()}')

        # move to RQ Worker
        blockUtilities.generateNextCircle()

        agentResponse['message'] = {
            'chainLength' : newBlock.getBlockHeight(),
            'lastBlock': newBlock.getBlockHash(),
            "circleDistance" : newBlock.getCircleDistance(),
            'message': newBlock.getBlockComment(),
            "error": ("No error checking candidate block" + str(redisUtilities.getCandidateBlocks()))
        }
        return agentResponse

    #execute instruction
    def executeInstruction(self, instruction):
        #call blockstate to execute instruction
        return blockUtilities.executeInstruction(instruction)

    # add an instruction to this sets pool. checks structure in agent
    # then moves to block utilities to add the instruction to redis
    def processInstruction(self, instruction):
        agentResponse = {}

        # check hash
        validInstruction = blockUtilities.validateInstruction(instruction)
        if not validInstruction['return']:
            logging.debug(f'Instruction not valid: {instruction}')
            agentResponse['success'] = False
            agentResponse['message'] = validInstruction['message']
            return agentResponse

        #check if the instruction is already in the pool.  If so still return True as not error 
        if redisUtilities.hasInstruction(instruction['instructionHash']):
            logging.info(f'Received instruction already have')
            agentResponse['success'] = True
            agentResponse['message'] = 'Instruction already in pool'
            return agentResponse

        # if not already in the pool add to the block state
        blockUtilities.addInstruction(instruction)

        agentResponse['message'] = "Instruction added"
        agentResponse['success'] = True

        return agentResponse


    # part 2 : gets and sets

    def getLastBlock(self):

        try:
            return {
                'lastBlock': redisUtilities.getBlockHash(),
                'blockHeight': redisUtilities.getBlockHeight(),
                'circleDistance': redisUtilities.getCircleDistance()
                }

        except RedisError as error:
            return f"Redis error: {error}"

    # returns the owner of the agent with the id claimed
    def getOwner(self):
        try:
            return redisUtilities.getOwnerID()
        except RedisError as error:
            return f"Redis Error getting owner ID: {error}"

    # returns the level of the agent
    def getLevel(self):
        try:
            return redisUtilities.getLevel()
        except RedisError as error:
            return f"Redis Error getting agent's level: {error}"

    def getPrivateKey(self):
        return self.agentPrivateKey

    def setPrivateKey(self, privateKey):
        self.agentPrivateKey = privateKey
        return

    def getConfig(self):
        try:
            agentConfig = {}
            agentConfig['level'] = redisUtilities.getLevel()
            agentConfig['agentIdentifier'] = self.agentID
            agentConfig['owner'] = redisUtilities.getOwnerID()
            agentConfig['signedIdentifier'] = redisUtilities.getSignedIdentifier()
            agentConfig['agentPrivateKey'] = self.agentPrivateKey

            return agentConfig
        except RedisError as error:
            return f"Redis Error getting agent's configuration: {error}"

    def getEntityList(self):
        try:
            return redisUtilities.getEntityList()
        except RedisError as error:
            return f"error returning entity list: {error}"

    def getCandidateBlocks(self):
        try:
            return redisUtilities.getCandidateBlocks()
        except RedisError as error:
            return f"error returning candidate blocks: {error}"

    # returns the list of attributes the entity has.  Hardcoded to test
    # TODO: work out the get and set attribute sections
    def getAttributes(self):
        return ['wallets.default.balance']

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

    # version 1 possible redundant or undated code. TODO: Review this section

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

    # Routine to get the current instruction pool we dont test convergence, any following agent can get this to populate their pool
    def instructionPool(self):
        logging.debug(f'In instructionPool')
        agentResponse = {}

        # Need to get the merkle root from the instruction pool. - I
        instruction_hashes = redisUtilities.getInstructionHashes()
        hashMerkle = encryptionUtilities.returnMerkleRoot(instruction_hashes)
        hashSigned = encryptionUtilities.ignMessage(hashMerkle,self.agentPrivateKey)
        agentResponse['message'] = {
                 'merkleRoot': hashMerkle,
                 'signed':hashSigned,
                 'hashes':list(instruction_hashes)
               }
        agentResponse['success'] = True
        return agentResponse
