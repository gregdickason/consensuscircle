import json
import copy
from bisect import bisect_left
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import redis
from rq import Queue
from globalsettings import blockSettings
import ccExceptions

import logging.config

ENCODING = 'utf-8'

red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)

def getCandidateBlocks():
    return list(red.smembers("candidateBlocks"))

def getCandidateBlock(blockID):
    if red.sismember("candidateBlocks", blockID) == 1:
        return json.loads(red.get("candidateBlocks:" + blockID))
    else:
        raise RedisError(f'there is no candidate block with id {blockID}')

def remCandidateBlock(blockID):
    # TODO: put in a lua to execute atomically?
    if red.sismember("candidateBlocks", blockID) == 1:
        block = json.loads(red.get("candidateBlocks:" + blockID))
        red.srem("candidateBlocks", blockID)
        return block
    else:
        raise RedisError(f'there is no candidate block with id {blockID}')

def getBlockHash():
    return red.hget("state", "latestBlock")

def getOutputMatrix(id=None):
    if id == None:
        return json.loads(red.hget(red.hget("state", "latestBlock"), "outputMatrix"))
    elif red.sismember("blockSet", id) == 1:
        return json.loads(red.hget(id, "outputMatrix"))
    else:
        raise RedisError(f'there is no block with id {id}')

def getPublicKey(id):
    # is this an agent or an entity?
    logging.info(f"blockstate.getPublicKey Called with hash {id}")
    if (red.sismember("entities", id) == 1) or (red.sismember("agents", id) == 1) or (red.sismember("owners", id) == 1):
        return red.hget(id, "publicKey")
    else:
        raise RedisError(f'there is no agent, entity or owner with id {id}')

#  get Attribute on an entity.
def getAttribute(entity, attribute):
    logging.debug(f'blockState.getAttribute: Getting attribute {attribute} from entity {entity}')

    if red.sismember("entities", entity) == 0:
        return "ERROR: invalid entity ID"
    try:
        return(red.hget(entity, attribute))
    except:
        return ''

# Check if an instruction is already in the pool.  We dont care if already processed into a block
def hasInstruction(hash):
    logging.debug(f'Checking if {hash} is in pool')
    if red.hget('instructionPool', hash):
        return True
    return False

# gets the instructionHashes stored in redis that are not deleted. These are valid for a block
def getInstructionHashes():
    # return the list of hashes in the instructionUnprocessedPool
    insList = list(red.smembers('instructionUnprocessedPool'))
    logging.debug(f'list of instructions returned is {insList}')
    return insList

# gets the instruction.  Again dont care if in a block
def getInstruction(hash):
    instruction = json.loads(red.hget("instructionPool", hash))

    if instruction:
        return instruction
    else:
        raise RedisError(f'there is no instruction with hash {hash}')

def getInstructionLuaHash(name):
    if red.sismember("instructions", name) == 1:
        return red.hget("instruction:" + name, "luaHash")
    else:
        raise RedisError(f"no instruction by name {name}")

def getInstructionKeys(name):
    if red.sismember("instructions", name) == 1:
        return json.loads(red.hget("instruction:" + name, "keys"))
    else:
        raise RedisError(f"no instruction by name {name}")

def getInstructionArgs(name):
    if red.sismember("instructions", name) == 1:
        return json.loads(red.hget("instruction:" + name, "args"))
    else:
        raise RedisError(f"no instruction by name {name}")

def getInstructionNames():
    return list(red.smembers("instructions"))

def getAttributes(id):
    if red.sismember("entities", id) == 1:
        return list(red.hkeys(id))
    else:
        return RedisError(f"no entity with id {id}")

def getEntity(entity):
    logging.debug(f'Getting entity {entity} in blockState)')

    if red.sismember("entities", entity) == 1:
        return red.hgetall(entity)

    logging.debug(f'ERROR: no entity with ID {entity} in blockState)')
    raise RedisError(f'there is no entity with id {entity}')

def getEntityList():
    return list(red.smembers("entities"))

def getDetailedBlock(id):
    # checking block exists
    if not blockExists(id):
        raise RedisError(f'there is no block with id {id}')
        # throw an exception

    filePath = red.hget(id, "filePath")
    with open(filePath) as json_data:
        block = json.load(json_data)

    # add this in once you have moved off dummy settings and finalised
    # block structure
    # bSettings = blockSettings()
    # if not all(k in block for k in bSettings):
    #     return "ERROR: Block file has been corrupted"
        # throw an exception

    return block

def getHeightDiff(id):
    # from the current block to the the input id block
    try:
        prevBlock = getPreviousBlock(red.hget("state", "latestBlock"))
    except RedisError:
        raise RedisError(f'issues getting height difference because of previous blocks not existing')

    height = 1
    while (prevBlock != id):
        height = height + 1
        prevBlock = getPreviousBlock(prevBlock)

    return height

def getWeightedCircleDistance(id):
    # currently based on the assumption of an alternate block chain of depth 1
    prevBlock = getPreviousBlock(red.hget("state", "latestBlock"))
    height = 1
    currCircleDistance = int(red.hget(red.hget("state", "latestBlock"), "circleDistance"),16)
    sumCircleDistance = currCircleDistance

    while (prevBlock != id):
        height = height + 1
        sumCircleDistance= sumCircleDistance + getCircleDistance(prevBlock)
        prevBlock = getPreviousBlock(prevBlock)

    weightedCircleDistance = sumCircleDistance/height

    return weightedCircleDistance

def blockExists(id):
    if (red.sismember("blockSet", id) == 0):
        return False
    else:
        return True

def getBlockHeight(id=None):
    if id == None:
        return int(red.hget(red.hget("state", "latestBlock"), "blockHeight"))
    elif red.sismember("blockSet", id) == 1:
        return (int(red.hget(id, "blockHeight")))
    else:
        raise RedisError(f'there is no block with id {id}')

def getCircleDistance(id=None):
    if id == None:
        return int(red.hget(red.hget("state", "latestBlock"), "circleDistance"),16)
    elif red.sismember("blockSet", id) == 1:
        return (int(red.hget(id, "circleDistance"),16))
    else:
        raise RedisError(f'there is no block with id {id}')

def getPreviousBlock(id=None):
    if id == None:
        prevBlock = red.hget(red.hget("state", "latestBlock"), "previousBlock")
    elif red.sismember("blockSet", id) == 1:
        prevBlock = red.hget(id, "nextBlock")
    else:
        # to do perhaps through an exception here
        raise RedisError(f'there is no block with id {id}')

    if prevBlock == "None":
        return None
    else:
        return prevBlock

def getNextBlock(id=None):
    if id == None:
        nextBlock = red.hget(red.hget("state", "latestBlock"), "nextBlock")
    elif red.sismember("blockSet", id) == 1:
        nextBlock = red.hget(id, "nextBlock")
    else:
        # to do perhaps through an exception here
        raise RedisError(f'there is no block with id {id}')

    if nextBlock == "None":
        return None
    else:
        return nextBlock

def getGenesisHash():
    return red.hget("state", "genesisBlock")

def setMyID(id):
    red.hset("state", "myID", id)
    return

def getMyID():
    return red.hget("state", "myID")

def getOwnerID(id=None):
    if id == None:
        return red.hget(red.hget("state", "myID"), "ownerID")
    elif red.sismember("agents", id) == 1:
        return red.hget(id, "ownerID")
    else:
        raise RedisError(f'there is no owner with id {id}')

def getSignedIdentifier(id=None):
    if id == None:
        return red.hget(red.hget("state", "myID"), "signedID")
    elif red.sismember("agents", id) == 1:
        return red.hget(id, "signedID")
    else:
        raise RedisError(f'there is no agent with id {id}')

def getLevel(id=None):
    if id == None:
        return red.hget(red.hget("state", "myID"), "level")
    elif red.sismember("agents", id) == 1:
        return red.hget(id, "level")
    else:
        raise RedisError(f'there is no agent with id {id}')

# def setRandomMatrix(id, randomMatrix):
#     red.hset(id, "randomMatrix", json.dumps(randomMatrix))
#     return
#
# def getRandomMatrix(id=None):
#     if id == None:
#         return red.hget(red.hget("state", "myID"), "randomMatrix")
#     elif red.sismember("agents", id) == 1:
#         return red.hget(id, "randomMatrix")
#     else:
#         return "ERROR: invalid ID"
#
# def setSeed(id, seed):
#     red.hset(id, "randomMatrix", json.dumps(seed))
#     return
#
# def getSeed(id=None):
#     if id == None:
#         return red.hget(red.hget("state", "myID"), "seed")
#     elif red.sismember("agents", id) == 1:
#         return red.hget(id, "seed")
#     else:
#         return "ERROR: invalid ID"
#
# def setRandomMatrixHash(id, hash):
#     red.hset(id, "randomMatrixHash", json.dumps(hash))
#     return
#
# def getRandomMatrix(id=None):
#     if id == None:
#         return red.hget(red.hget("state", "myID"), "randomMatrixHash")
#     elif red.sismember("agents", id) == 1:
#         return red.hget(id, "randomMatrixHash")
#     else:
#         return "ERROR: invalid ID"
