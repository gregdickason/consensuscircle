import json
import copy
from bisect import bisect_left
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import redis
from rq import Queue
from convergenceProcessor import blockConvergeAndPublish

import logging.config

ENCODING = 'utf-8'

# Holds the blockState for the current chain we are following that we believe is valid.  We can change this if presented with a better block or chain (Where depth weighted chain distance is lower)
# This class is specific to the environment in which the agent is running.  Same method signatures but differnet implementations per environment
# This is for local agent with all settings and long term storage in redis.
# Other versions uses cloud technologies (eg S3)
class blockState:
  def __init__(self):
    # UNCOMMENT LINE BELOW TO RUN LOCALLY AND COMMETN LINE 26
    # self.red = redis.StrictRedis(host='localhost', port=6379, db=0, charset=ENCODING, decode_responses=True)

    self.red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)
    #redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

    self.pipe = self.red.pipeline()

    # TODO confirm that the local redis instance is running and has the blockstate loaded: agents, entities, etc
    # TODO - remove currentBlockchainstate.  Store to redis.
    with open('currentBlockChainState.json') as json_data:
        self.blockState = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed and also that this block is valid in the context of previous blocks
    logging.debug(f'Blockchain State is {self.blockState}')
    self.outputMatrix = self.blockState['blockRandomMatrix']
    self.merkleTreeRoot = self.blockState['blockMerkleRoot']  # Random for simulation
    self.blockHash = self.blockState['blockHash']   # Hash of the highest block in chain
    self.blockHeight = self.blockState['blockHeight']
    self.depthWeightedChainDistancePreviousBlock = self.blockState['depthWeightedChainDistancePreviousBlock']
    self.root = '5000'   # Used to root the current state in redis

    # add in current_instructions with get / set mechanisms that then link to REDIS here
    self.current_instructions = {}
    self.current_instructionHandlers = {}
    self.current_entities = {}

    # Load entities - stored in redis.  This will get unweildly
    # TODO: store long term in redis or some compact json form (binary json)
    for e in self.blockState['Entities']:
      with open('entities/' + e + '.json') as json_data:
        entity = json.load(json_data)
        logging.debug(f'loaded {entity}')
      self.current_entities[entity['Entity']] = entity


    logging.debug(f'\nprevious block convergence matrix is {self.outputMatrix}')
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

    # create the instructionPool object to store instructions
    # TODO implement the redlock algorithm for locking

  def executeInstruction(self, hash):
      instruction = json.loads(self.red.get('instructionPool:'+ hash))
      #instruction = self.current_instructions[hash]

      logging.debug(f'\n instruction retrieved is {instruction}\n')

      args = instruction['instruction']['args']
      keys = instruction['instruction']['keys']
      luaHash = instruction['instruction']['luaHash']

      output = self.red.execute_command("EVALSHA", luaHash, len(keys), *(keys+args))

      return output

  # Manage the instruction pool
  def addInstruction(self, instruction):

    # TODO remove insOut and current_instructions - only store in redis?
    insOut = instruction
    hash = instruction['instructionHash']

    logging.debug(f'\nwriting {hash} to redis\n')
    self.current_instructions[hash] = insOut

    # Store to redis - batch as we are writing to both the keys store and the instructionPool

    self.pipe.set('instructionPool:' + hash, json.dumps(insOut))
    self.pipe.sadd('instructionHashes',hash)
    self.pipe.execute()

    return

  # Check if an instruction is already in the pool
  def hasInstruction(self,hash):
    logging.debug(f'Checking if {hash} is in pool')
    if self.red.get('instructionPool:' + hash):
      return True
    return False

  # gets the instructionHashes stored in redis
  def getInstructionHashes(self):
    # return the list of hashes in the instructionhashes
    insList = list(self.red.smembers('instructionHashes'))
    logging.debug(f'list of instructions returned is {insList}')
    return insList


  # Manage the instructionHandler pool
  def addInstructionHandler(self, instructionHandler, hash,sign):

    logging.debug(f'\nwriting {hash} to redis\n')
    insHanOut = {}
    insHanOut['instructionHandlerHash'] = hash
    insHanOut['sign'] = sign
    insHanOut['instructionHandler'] = instructionHandler
    self.current_instructionHandlers[hash] = insHanOut

    # Store to redis

    self.red.set('instructionHandlerPool:' + hash, json.dumps(insHanOut))

    return

  def getInstructionList(self):
    logging.debug(f'Returning instructions for getInstructionList: {self.current_instructions.values()}')
    return self.current_instructions.values()

  def getInstructionHandlerList(self):
    logging.debug(f'Returning instructionHandlerss for getInstructionHandlerList: {self.current_instructionHandlers.values()}')
    return self.current_instructionHandlers.values()


  # All entities in memory
  # TODO: use redis to store enties and persist to disk when needed. (or as backup store on Redis)
  def getEntity(self, entity):
    logging.debug(f'Getting entity {entity} in blockState)')
    try:
      return self.current_entities[entity]
    except:
      # TODO throw exception and handle in Agent
      return ''

  def getEntityList(self):
      return list(self.current_entities.keys())
      
  #  get Attribute on an entity.  
  def getAttribute(self, entity, attribute):
    logging.debug(f'blockState.getAttribute: Getting attribute {attribute} from entity {entity}')
    try: 
      return(self.red.hget(entity, attribute))
    except:
      return ''

  # Send a message to an agent using their pkey.  We do this abstracted so does not have to be through HTTP for production clients (agents can set their comms mechanism)
  def sendMessage(self,agentID, message, function):
    logging.debug(f'\nGot {message}  to send\n')

    if agentID in self.agentURLs.keys():
      request = Request(self.agentURLs[agentID] + '/' + function)
      request.add_header('Content-Type','application/json; charset=utf-8')
      jsondata = json.dumps(message)
      jsondataasbytes = jsondata.encode('utf-8')
      request.add_header('Content-Length', len(jsondataasbytes))
      logging.debug(f'\nRequest is {request}  \n')
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

    # you dont need to make a new redis connection you can use the existing one that is defined above (line 26)
    q = Queue('5000', connection=self.red)  # send to default queue for now
    jsondata = json.dumps(data)
    job = q.enqueue(blockConvergeAndPublish, jsondata)
    logging.debug(f'Sent {jsondata} - on default queue')
    return



  def getPubKey(self, pubKeyHash):
    # is this an agent or an entity?
    if pubKeyHash in self.agentPublicKeys:
      return self.agentPublicKeys[pubKeyHash]
    elif pubKeyHash in self.current_entities:
      logging.info("HERE HERE HERE")
      return self.current_entities[pubKeyHash]['PublicKey']
    else:
      #TODO throw errors / error checking
      return

  # Distance calculations for finding the nearest agent to a number for a level.  This is not optimised as will be in a data structure in Lambda
  # currently it is order of N which will get very big.  Needs to be rewritten with binHashTree (TODO)
  # Note this is in memory for the test version that this blockstate manages.  Different implementation in cloud versions
  def nextCircle(self,lastBlockMatrix, excludedAgents):
    nextcircle, bIndex = [],0
    logging.debug(f'in next circle with lastBlockMatrix: {lastBlockMatrix}, excludedAgents: {excludedAgents}')
    # TODO - efficiency of deepcopy will not scale.  Different approach excluding agents needed.  Code this
    self.templevel = copy.deepcopy(self.level)
    logging.debug(f'templevel is {self.templevel}')

    # remove all the excludedAgents per level:
    for level in excludedAgents:
      levelName = level['level']
      for i in level[levelName]:
        logging.debug(f'removing {i}')
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

      logging.debug(f'takeClosest: {myList} and {myNumber}')
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
