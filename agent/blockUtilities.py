import json
import copy
from bisect import bisect_left
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import redis
from rq import Queue
import convergenceProcessor
from globalsettings import instructionInfo, blockSettings

import logging.config

ENCODING = 'utf-8'

red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)

# Holds the blockState for the current chain we are following that we believe is valid.  We can change this if presented with a better block or chain (Where depth weighted chain distance is lower)
# This class is specific to the environment in which the agent is running.  Same method signatures but differnet implementations per environment
# This is for local agent with all settings and long term storage in redis.
# Other versions uses cloud technologies (eg S3)
def addNewBlock(newBlock):
    # update redis and run instructions (LUA Script)
    id = newBlock.getBlockHash()

    newBlockPipe = red.pipeline(transaction=True)
    newBlockPipe.sadd("blocks", id)
    newBlockPipe.hset("state", "latestBlock", id)
    newBlockPipe.hset(id, "previousBlock", newBlock.getPreviousBlock())
    newBlockPipe.hset(newBlock.getPreviousBlock(), "nextBlock", id)
    newBlockPipe.hset(id, "nextBlock", "None")
    newBlockPipe.hset(id, "circleDistance", newBlock.getCircleDistance())
    newBlockPipe.hset(id, "blockHeight", newBlock.getBlockHeight())
    newBlockPipe.hset(id, "outputMatrix", json.dumps(newBlock.getOutputMatrix()))

    instructions = newBlock.getInstructions()
    instructionSettings = instructionInfo()

    for instruction in instructions:
        args = instruction['instruction']['args']
        keys = instruction['instruction']['keys']
        luaHash = instructionSettings.getInstructionHash(instruction['instruction']['name'])
        newBlockPipe.evalsha(luaHash, len(keys), *(keys+args))

    # write out and add filePath
    filePath = "blocks/" + id + ".json"
    blockFile = open(filePath, 'w')
    blockFile.write(json.dumps(vars(newBlock)))
    blockFile.close()
    newBlockPipe.hset(id, "filePath", filePath)

    newBlockPipe.execute()

    # if block id exist in redis


    # if cant write file log - agent specific

    return

def executeInstruction(hash):
    instruction = json.loads(red.get('instructionPool:'+ hash))

    logging.debug(f'\n instruction retrieved is {instruction}\n')

    args = instruction['instruction']['args']
    keys = instruction['instruction']['keys']

    instructionSettings = instructionInfo()
    luaHash = instructionSettings.getInstructionHash(instruction['instruction']['name'])
    if luaHash == None:
        return 'ERROR: no instruction matches the given instructionName'

    output = red.execute_command("EVALSHA", luaHash, len(keys), *(keys+args))

    return output

def rollBack(to):
    # GREG TO DO
    #roll back the state to the block 'to'
    return "TODO"

def tryInstruction(hash):
    # GREG TO DO
    # instruction = getInstruction(hash)
    #
    # args = instruction['instruction']['args']
    # keys = instruction['instruction']['keys']
    #
    # instructionSettings = instructionInfo()
    # luaHash = instructionSettings.getInstructionHash(instruction['instruction']['name'])
    # if luaHash == None:
    #     return 'ERROR: no instruction matches the given instructionName'
    #
    # output = red.execute_command("EVALSHA", luaHash, len(keys), *(keys+args))

    return True

  # Manage the instruction pool
def addInstruction(instruction):

    # TODO remove insOut and current_instructions - only store in redis?
    insOut = instruction
    hash = instruction['instructionHash']

    addInstructionPipe = red.pipeline(transaction=True)

    logging.debug(f'\nwriting {hash} to redis\n')

    # Store to redis - batch as we are writing to both the keys store and the instructionPool
    addInstructionPipe.set('instructionPool:' + hash, json.dumps(insOut))
    addInstructionPipe.sadd('instructionHashes',hash)
    addInstructionPipe.execute()

    return

# Send a message to an agent using their pkey.  We do this abstracted so does not have to be through HTTP for production clients (agents can set their comms mechanism)
# def sendMessage(agentID, message, function):
#     logging.debug(f'\nGot {message}  to send\n')
#
#     if agentID in self.agentURLs.keys():
#         request = Request(self.agentURLs[agentID] + '/' + function)
#         request.add_header('Content-Type','application/json; charset=utf-8')
#         jsondata = json.dumps(message)
#         jsondataasbytes = jsondata.encode('utf-8')
#         request.add_header('Content-Length', len(jsondataasbytes))
#         logging.debug(f'\nRequest is {request}  \n')
#         try:
#             msgResponse = json.loads(urlopen(request,jsondataasbytes).read().decode('utf-8'))
#             logging.debug(f'\nGot valid response from sendMessage')
#             return (True, msgResponse)
#         except ConnectionRefusedError:
#             logging.error(f'\nGot connection refused\n')
#             return (False, 'Error - Agent not able to be connected to')
#         except:
#             logging.error(f'\nGot error {sys.exc_info()[0]}\n')
#             return (False, 'Error in communicating with Agent')
#     else:
#         logging.error(f'\nAgent not known\n')
#         return (False, 'Error - agent not known')   # TODO throw exception for this?


# postJob is internal and used to communicate to queue.  In the local implementation this is to a redis queue (pip install rq)
# Note if using redis on Windows need to run linux subsystem (https://docs.microsoft.com/en-us/windows/wsl/install-win10)
def postJob():
    # you dont need to make a new redis connection you can use the existing one that is defined above (line 26)
    q = Queue('5000', connection=red)  # send to default queue for now
    job = q.enqueue(convergenceProcessor.generateNextCircle)
    return
