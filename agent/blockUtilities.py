import json
import copy
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import redis
from rq import Queue
import convergenceProcessor
from globalsettings import instructionInfo, blockSettings
import ccExceptions

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
    newBlockPipe.lpush("blocks", id)
    newBlockPipe.sadd("blockSet", id)

    # this could be better - use trim? but then you dont get back the block hash to remove
    if (red.llen("blocks") >= int(red.hget("state", "numBlocksStored"))):
        blockToRemove = red.rpop("blocks")
        red.srem("blockSet", blockToRemove)
        red.delete(blockToRemove)

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
        hash = instruction['instructionHash']
        executeInstruction(hash, newBlock.getBlockHeight(), newBlockPipe)
          # Failure in processing the block.  Abort and reject the block


    newBlockPipe.hset(id, "filePath", filePath)

    # execute the pipe.  This may result in failures (unlikely if the block is properly formed but possible).
    # read https://pypi.org/project/redis/ and https://redis.io/topics/transactions  which runs transaction even with failures!
    # we dont throw error in lua?  (https://redis.io/commands/eval)
    output = newBlockPipe.execute()

    # Any failure?  Will be present as a '0' in the output array.  This list search could be slow so may need optimisation
    # TODO: test this comprehensively
    # TODO: check if we need to test for other failures sucah as the hset commands
    if '0' in output:
      # Get the index and the error reason after that and throw a block exception
      errorOutput = output.index('0') + 1
      logging.error(f'Block failed with 1 or more instructions not valid.  Error {output[errorOutput]}')
      # Rollback the block
      # TODO: check if rollback fails.  What do we do then?
      rollBack(newBlock.getPreviousBlock())
      raise BlockError(output[errorOutput], id, newBlock.getPreviousBlock())

    # write out and add filePath
    # TODO: should be a helper method to hide underlying filesystem (might write to AWS or s3).  Also write this first not after redis execution - discard if not in chain through a cleanup routine?
    filePath = "blocks/" + id + ".json"
    blockFile = open(filePath, 'w')
    blockFile.write(json.dumps(vars(newBlock)))
    blockFile.close()


    return

def executeInstruction(hash, blockHeight=0, pipe=None):
    # This routine is not used directly in production but in setup and for testing - Only part of mined block
    instruction = getInstruction(hash)

    if instruction == None:
      return 'ERROR: no instruction with {hash} in pool'

    logging.debug(f'\n instruction retrieved is {instruction}\n')

    # TODO: confirm instruction has a unique nonce (in LUA) - and extended from previous one
    # TODO - need to check syntax of instruction (number fields).  Fail if not setup properly
    # TODO create InstructionException and throw this for the different reasons rather than return False.  Can then propogate the LUA reasons for failures
    args = []
    keys = []

    args.append('mined')
    args.append(instruction['instructionHash'])
    # append blockheight - we dont create a rollback state
    # TODO update scripts for this
    args.append(blockHeight - 1)
    args.extend(instruction['instruction']['args'])

    keys.append(instruction['instruction']['sender'])
    keys.extend(instruction['instruction']['keys'])

    instructionSettings = instructionInfo()
    luaHash = instructionSettings.getInstructionHash(instruction['instruction']['name'])
    if luaHash == None:
      return 'ERROR: no instruction matches the given instructionName'

    if pipe == None:
        # this is not in a block so just execute the instruction
        output = red.evalsha(luaHash, len(keys), *(keys+args))
        if output[0] == 0:
          logging.error(f'ERROR in executing instruction : {output[1]}')
          return False
    else:
        # Queue in the pipeline - no response as not executed
        pipe.evalsha(luaHash, len(keys), *(keys+args))

    return True

def rollBack(to):
    # setup the block pipe to queue the transaction
    pipe = red.pipeline(transaction=True)

    # First rollback the state
    # Currently hardcoded the sha but TODO needs to be in a set of scripts.  (Not an instruction rather a helper script)
    luaHash = 'fd2ae4a1a8c058bd2ff8f09b77c0e186d39e178c'
    keys = []
    args = []
    args.append(to)

    # Rollback the state through a LUA script so is 100% pass / fail on state update
    pipe.evalsha(luaHash, len(keys), *(keys+args))

    # Now rollback the blocks:
    currBlock = redisUtilities.getBlockHash()
    endBlock = red.rpop("blocks")
    red.rpush("blocks", endBlock)

    while currBlock != to:
        pipe.lrem("blocks", "0", currBlock)
        pipe.srem("blockSet", currBlock)
        if (red.llen("blocks") >= int(red.hget("state", "numBlocksStored"))):
            # if not full size the block will already be in the block set
            endBlock = redisUtilities.getPreviousBlock(endBlock)
            pipe.rpush("blocks", endBlock)
            pipe.sadd("blockSet", endBlock)
        currBlock = redisUtilities.getPreviousBlock(currBlock)

    pipe.hset("state", "latestBlock", to)
    pipe.hset(to, "nextBlock", "None")

    # provided that the block is in the last n blocks stored in redis this will all
    # be already in redis so it does not need to be readded.
        # newBlockPipe.hset(id, "previousBlock", newBlock.getPreviousBlock())
        # newBlockPipe.hset(newBlock.getPreviousBlock(), "nextBlock", id)
        # newBlockPipe.hset(id, "circleDistance", newBlock.getCircleDistance())
        # newBlockPipe.hset(id, "blockHeight", newBlock.getBlockHeight())
        # newBlockPipe.hset(id, "outputMatrix", json.dumps(newBlock.getOutputMatrix()))

    # execute.
    pipe.execute()

    return True

def tryInstruction(hash):
    # Test that this instruction works in a candidate block.
    # TODO - clean up the state once finalised list of instructions in the candidate block

    instruction = getInstruction(hash)

    if instruction == None:
      return 'ERROR: no instruction with {hash} in pool'

    args = []
    keys = []

    args.append('mining')
    args.append(instruction['instructionHash'])
    args.extend(instruction['instruction']['args'])

    keys.append(instruction['instruction']['sender'])
    keys.extend(instruction['instruction']['keys'])

    logging.debug(f'Instruction retrieved is {instruction}\n')

    instructionSettings = instructionInfo()
    luaHash = instructionSettings.getInstructionHash(instruction['instruction']['name'])
    if luaHash == None:
        logging.error(f'No instruction matches the given instruction hash: {hash}')
        return False

    output = red.execute_command("EVALSHA", luaHash, len(keys), *(keys+args))
    if int(output[0]) == 0:
      return False # we have rejected the instruction.  Need to remove from block
    else:
      return True


    # Get an instruction - return null if not in pool
def getInstruction(instructionHash):
    logging.debug(f'get instruction {instructionHash}')

    if red.exists('instructionPool:'+ instructionHash):
      instruction = json.loads(red.get('instructionPool:'+ instructionHash))
      return instruction
    else:
      logging.info(f'Attempting to get instruction from Pool that is not in pool: {instructionHash}')
      return None


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
def generateNextCircle():

    # convergenceProcessor.generateNextCircle()
    # you dont need to make a new redis connection you can use the existing one that is defined above (line 26)
    q = Queue(connection=red)  # send to default queue for now
    job = q.enqueue(convergenceProcessor.generateNextCircle)
    logging.info("job id is:" + job.get_id())

    return
