import json
import copy
from bisect import bisect_left
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import redis
from rq import Queue
from convergenceProcessor import blockConvergeAndPublish

import logging.config

# Holds the blockState for the current chain we are following that we believe is valid.  We can change this if presented with a better block or chain (Where depth weighted chain distance is lower)
# This class is specific to the environment in which the agent is running.  Same method signatures but differnet implementations per environment
# This is for local agent with all settings and long term storage in json files, using redis and rejson for queues and instructionPool.  
# Other versions uses cloud technologies (eg S3) and do not always load state into memory
class blockState:
  def __init__(self):
    with open('currentBlockChainState.json') as json_data:
        self.blockState = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
    logging.info(f'Blockchain State is {self.blockState}')
    self.outputMatrix = self.blockState['blockRandomMatrix']
    self.merkleTreeRoot = self.blockState['blockMerkleRoot']  # Random for simulation 
    self.blockHash = self.blockState['blockHash']   # Hash of the highest block in chain
    self.blockHeight = self.blockState['blockHeight']
    self.depthWeightedChainDistancePreviousBlock = self.blockState['depthWeightedChainDistancePreviousBlock']
    self.root = '5000'   # Used to root the current state in redis
    
    # add in current_instructions with get / set mechanisms that then link to REDIS here
    self.current_instructions = {}
    self.current_instructionHandlers = {}
    
    logging.info(f'\nprevious block convergence matrix is {self.outputMatrix}')
    # get the agent public keys into a binary matrix
    
    self.agents = self.blockState['agents']
    self.agentPublicKeys = {}
    self.agentURLs = {}
    
    # define the levels we accept and the number per level:
    self.agentLevels = {'founder':1,'defender':1,'protector':1,'contributor':2,'member':0}
    
    # Looks for levels.  This is not efficient but will not be used in production (where these will be DB lookups)
    # storing in lists so we can sort and find nearest matches.  Will slow down if we need to remove some numbers (eg if nearest not available)
    self.level = {}
    self.level['founder'] = [] 
    self.level['defender'] = [] 
    self.level['protector'] = [] 
    self.level['contributor'] = [] 
    self.level['member'] = []
    
    for e in self.agents:
      self.agentPublicKeys[e['agentID']] = e['agentPubKey']
      self.level[e['level']].append(e['agentID'])
      self.agentURLs[e['agentID']] = e['agentURL']
    
    # sort the level lists to make it more efficient and use takeClosest (note sorting is highly optimised in Python)
    for e in self.level:
      self.level[e].sort()
    
    # setup rejson as our in memory store.  
    # TODO - store the data in redis on shutdown of redis
    self.red = redis.StrictRedis(host='localhost', port=6379, db=0)
    
    # create the instructionPool object to store instructions
    # TODO implement the redlock algorithm for locking 
    
  # Manage the instruction pool 
  def addInstruction(self, instruction, hash,sign):
    insOut = {}
    insOut['instructionHash'] = hash
    insOut['sign'] = sign
    insOut['instruction'] = instruction
    
    logging.info(f'\nwriting {hash} to redis\n')
    self.current_instructions[hash] = insOut
    
    # Store to redis
    self.red.set('instructionPool:' + hash, json.dumps(insOut))
    
    return
    
  # Manage the instructionHandler pool 
  def addInstructionHandler(self, instructionHandler, hash,sign):
    
    logging.info(f'\nwriting {hash} to redis\n')
    insHanOut = {}
    insHanOut['instructionHandlerHash'] = hash
    insHanOut['sign'] = sign
    insHanOut['instructionHandler'] = instructionHandler
    self.current_instructionHandlers[hash] = insHanOut
    
    # Store to redis
    self.red.set('instructionHandlerPool:' + hash, json.dumps(insHanOut))
    
    return

  def getInstructionList(self):
    logging.info(f'Returning instructions for getInstructionList: {self.current_instructions.values()}')
    return self.current_instructions.values()

  def getInstructionHandlerList(self):
    logging.info(f'Returning instructionHandlerss for getInstructionHandlerList: {self.current_instructionHandlers.values()}')
    return self.current_instructionHandlers.values()

  
  # Send a message to an agent using their pkey.  We do this abstracted so does not have to be through HTTP for production clients (agents can set their comms mechanism)
  def sendMessage(self,agentID, message, function):
    logging.info(f'\nGot {message}  to send\n')
             
    if agentID in self.agentURLs.keys():
      request = Request(self.agentURLs[agentID] + '/' + function)
      request.add_header('Content-Type','application/json; charset=utf-8')  
      jsondata = json.dumps(message)
      jsondataasbytes = jsondata.encode('utf-8')
      request.add_header('Content-Length', len(jsondataasbytes))
      logging.info(f'\nRequest is {request}  \n')
      try:
        msgResponse = json.loads(urlopen(request,jsondataasbytes).read().decode('utf-8'))
        logging.debug(f'\nGot valid response from sendMessage')
        return (True, msgResponse)
      except ConnectionRefusedError:
        logging.error(f'\nGot connection refused\n')
        return (False, 'Error - Agent not able to be connected to')
      except:
        logging.error(f'\nGot error {sys.exc_info()[0]}\n')
        return (False, 'Error in communicating with Agent')
    else: 
      logging.error(f'\nAgent not known\n')
      return (False, 'Error - agent not known')   # TODO throw exception for this? 

  
  # postJob is internal and used to communicate to queue.  In the local implementation this is to a redis queue (pip install rq)
  # Note if using redis on Windows need to run linux subsystem (https://docs.microsoft.com/en-us/windows/wsl/install-win10)
  def postJob(self,data):
    redis_conn = redis.Redis()
    # TODO check if need to do 1 call for Redis not here
    q = Queue('5000', connection=redis_conn)  # send to default queue for now
    jsondata = json.dumps(data)
    job = q.enqueue(blockConvergeAndPublish, jsondata)
    logging.info(f'Sent {jsondata} - on default queue')
    return
     

  
  def getPubKey(self, pubKey):
    return self.agentPublicKeys[pubKey]
  
  
  # Distance calculations for finding the nearest agent to a number for a level.  This is not optimised as will be in a data structure in Lambda
  # currently it is order of log(n) 
  # Note this is in memory for the test version that this blockstate manages.  Different implementation in cloud versions
  def nextCircle(self,lastBlockMatrix, excludedAgents):
    nextcircle, bIndex = [],0
    logging.info(f'in next circle with lastBlockMatrix: {lastBlockMatrix}, excludedAgents: {excludedAgents}') 
    self.templevel = copy.deepcopy(self.level)
    logging.info(f'templevel is {self.templevel}')
    
    # remove all the excludedAgents per level:
    for level in excludedAgents:
      levelName = level['level']
      for i in level[levelName]:
        logging.info(f'removing {i}')
        self.templevel[levelName].remove(i)
    
    # find next agent and delete from level so cant be chosen twice:    
    for i in self.agentLevels.keys():
      j = 0
      while j < self.agentLevels[i]:
        # note deletes the templevel agent in the takeClosest method
        nextAgent = self.takeClosest(self.templevel[i],lastBlockMatrix[bIndex])
        nextcircle.append(nextAgent)
        self.templevel[i].remove(nextAgent)
        bIndex += 1
        j += 1
    return nextcircle   
        
  
  # Utility functions we dont need when using a database / dynamoDB etc:
  # from https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value/12141511#12141511
  def takeClosest(self,myList, myNumber):
      """
      Assumes myList is sorted. Returns closest value to myNumber.
      If two numbers are equally close, return the smallest number.
      Ignore anything in the excludedList
      """
      
      logging.info(f'takeClosest: {myList} and {myNumber}')  
      # for efficiency could remove before returning (rather than search through twice on the return call)      
      pos = bisect_left(myList, myNumber)
      if pos == 0:
          return myList[0]
      if pos == len(myList):
          return myList[-1]
      before = myList[pos - 1]
      after = myList[pos]
      if int(after,16) - int(myNumber,16) < int(myNumber,16) - int(before,16):
         return after
      else:
         return before

