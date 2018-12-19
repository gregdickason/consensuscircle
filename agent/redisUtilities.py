import json
import copy
from bisect import bisect_left
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import redis
from rq import Queue
from globalsettings import instructionInfo, blockSettings

import logging.config

ENCODING = 'utf-8'

red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)

def getBlockHash():
    return red.hget("state", "latestBlock")

def getOutputMatrix(id):
    if id == None:
        return json.loads(red.hget(red.hget("state", "latestBlock"), "outputMatrix"))
    elif red.sismember("blocks", id) == 1:
        return json.loads(red.hget(id, "outputMatrix"))
    else:
        return "ERROR: invalid ID"

def getPublicKey(id):
    # is this an agent or an entity?
    logging.info(f"blockstate.getPublicKey Called with hash {id}")
    if (red.sismember("entities", id) == 1) or (red.sismember("agents", id) == 1) or (red.sismember("owners", id) == 1):
        return red.hget(id, "publicKey")
    else:
        #TODO throw errors / error checking
        return

#  get Attribute on an entity.
def getAttribute(entity, attribute):
    logging.debug(f'blockState.getAttribute: Getting attribute {attribute} from entity {entity}')

    if red.sismember("entities", entity) == 0:
        return "ERROR: invalid entity ID"

    try:
        return(red.hget(entity, attribute))
    except:
        return ''

# Check if an instruction is already in the pool
def hasInstruction(hash):
    logging.debug(f'Checking if {hash} is in pool')
    if red.get('instructionPool:' + hash):
        return True
    return False

# gets the instructionHashes stored in redis
def getInstructionHashes():
    # return the list of hashes in the instructionhashes
    insList = list(red.smembers('instructionHashes'))
    logging.debug(f'list of instructions returned is {insList}')
    return insList

def getInstruction(hash):
    return json.loads(red.hget("instructionPool:" + hash))

def getEntity(entity):
    logging.debug(f'Getting entity {entity} in blockState)')

    if red.sismember("entities", entity) == 1:
        return red.hgetall(entity)

    logging.debug(f'ERROR: no entity with ID {entity} in blockState)')
    return "ERROR: No entity with that ID"

def getEntityList():
    return list(red.smembers("entities"))

def getDetailedBlock(id):
    # checking block exists
    if not blockExists(id):
        return "ERROR"
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
    prevBlock = getPreviousBlock(red.hget("state", "latestBlock"))
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
    if (red.sismember("blocks", id) == 0):
        return False
    else:
        return True

def getBlockHeight(id=None):
    if id == None:
        return int(red.hget(red.hget("state", "latestBlock"), "blockHeight"))
    elif red.sismember("blocks", id) == 1:
        return (int(red.hget(id, "blockHeight")))
    else:
        return "ERROR: invalid ID"

def getCircleDistance(id=None):
    if id == None:
        return int(red.hget(red.hget("state", "latestBlock"), "circleDistance"),16)
    elif red.sismember("blocks", id) == 1:
        return (int(red.hget(id, "circleDistance"),16))
    else:
        return "ERROR: invalid ID"

def getPreviousBlock(id=None):
    if id == None:
        prevBlock = red.hget(red.hget("state", "latestBlock"), "nextBlock")
    elif red.sismember("blocks", id) == 1:
        prevBlock = red.hget(id, "nextBlock")
    else:
        # to do perhaps through an exception here
        prevBlock = "ERROR"

    if prevBlock == "None":
        return None
    else:
        return prevBlock

def getNextBlock(id=None):
    if id == None:
        nextBlock = red.hget(red.hget("state", "latestBlock"), "nextBlock")
    elif red.sismember("blocks", id) == 1:
        nextBlock = red.hget(id, "nextBlock")
    else:
        # to do perhaps through an exception here
        nextBlock = "ERROR"

    if nextBlock == "None":
        return None
    else:
        return nextBlock

def getGenesisHash():
    return red.hget("state", "genesisBlock")

# ADD ERROR MANAGEMENT
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
        return "ERROR: invalid ID"

def getSignedIdentifier(id=None):
    if id == None:
        return red.hget(red.hget("state", "myID"), "signedID")
    elif red.sismember("agents", id) == 1:
        return red.hget(id, "signedID")
    else:
        return "ERROR: invalid ID"

def getLevel(id=None):
    if id == None:
        return red.hget(red.hget("state", "myID"), "level")
    elif red.sismember("agents", id) == 1:
        return red.hget(id, "level")
    else:
        return "ERROR: invalid ID"

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
