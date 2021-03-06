import requests
import json
import consensusEmulator
import redisUtilities
import blockUtilities
import encryptionUtilities
import logging.config
from bisect import bisect_left

import redis
from rq import Queue


with open('logConfig.json') as json_data:
    logDict = json.load(json_data)
    logging.config.dictConfig(logDict)

ENCODING = 'utf-8'
red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)

# This is the processor for converging the circle, it listens on a queue as convergence is asynchronous (non blocking).
# The agent does a full convergence as a single data packet with gossip protocol (see data structure as the reference)

# Test Initial implementation creates next block without convergence - signs off from all agents in circle

def generateNextCircle():

    logging.debug("in generateNextCircle")

    # should always be the latest block that you are generating the next circle from
    circle = nextCircle(redisUtilities.getOutputMatrix())  # No excluded agents for now, get matrix of last block

    logging.debug(f'next circle outputMatrix is {circle}')

    # Am I in the circle?

    if not (redisUtilities.getMyID() in circle):
        # what should happen if not in next circle?
        logging.info("I AM NOT IN THE NEXT CIRCLE.")
        return

    logging.debug("Agent is in next circle")
    # gather and check instructions
    possibleInstructions = redisUtilities.getInstructionHashes()
    logging.debug(f'possible instructions are {possibleInstructions}')
    validInstructions = []
    validInstructionHashes = []
    # TODO here: clear any mining pool from previous iterations.  (clearMining.lua script).  Hardcoded for now but put in redisUtilities
    luaHash = 'b5ef661e48d6306417d1f645c358f3d98a6148a1'
    red.evalsha(luaHash, 0)
    # TODO catch around this.  If instruction fails on a non matching script it should be removed.
    for instructionHash in possibleInstructions:
        if blockUtilities.tryInstruction(instructionHash):
            logging.debug('instruction was valid')
            validInstructionHashes.append(instructionHash)
            validInstructions.append(redisUtilities.getInstruction(instructionHash))

    logging.debug(f'valid instructions are: {validInstructionHashes}')
    if len(validInstructionHashes) == 0:
        logging.info("there are no valid instructions and so, no valid block")
        # TODO - do we broadcast no valid block?  Or do we pause and retry in 10s?
        return

    # TODO: global static (in Redis?) for random number size, agents in the CIRCLE
    myRandoms = [g for g in encryptionUtilities.getRandomNumbers(32, 5)]
    logging.debug(f'myRandoms are {myRandoms}')

    mySeed = encryptionUtilities.getRandomNumber(32)
    logging.debug(f'mySeed is {mySeed}')

    mySeededRandomHash = encryptionUtilities.getHashWithSeed(myRandoms,mySeed)
    logging.debug(f'seeded hash is {mySeededRandomHash}')

    convergenceHeader = {
              "previousBlock" : redisUtilities.getBlockHash(),
              "instructionsMerkleRoot" : encryptionUtilities.returnMerkleRoot(validInstructionHashes),
              "instructionCount" : len(validInstructions),
              "blockHeight" : (redisUtilities.getBlockHeight() + 1),
              "randomNumberHash": mySeededRandomHash
    }

    logging.debug(f'convergenceHeader is {convergenceHeader}')

    signature = encryptionUtilities.signMessage(encryptionUtilities.getHashofInput(convergenceHeader),redisUtilities.getMyPrivKey())

    logging.debug(f'signature is {signature}')

    blockSignatures = [{redisUtilities.getMyID() : signature}]
    logging.debug(f'blockSignatures is {blockSignatures}')
    proposedBlock = {
        "convergenceHeader" : json.dumps(convergenceHeader),
        "blockSignatures" :  blockSignatures,
        "instructions" : json.dumps(validInstructions),
        "broadcaster" : redisUtilities.getMyID()
    }

    logging.info(f'Proposed Block for initial convergence is {proposedBlock}')

    # Write these to blockchain?  (or after all done?)


    # TODO setup signature for convergence header


    # TODO create proposedBlock and convergence header.  Broadcast proposed block. Need to lookup addresses of the

    # TODO also update consensus emulator to emit new block type structure.

    # TODO update NODE to accumulate latest block (same convergence header) with all the random numbers

    # GREG: I think this is where we emulate the full block creation?
    approval = consensusEmulator.proposeConvergenceHeader(proposedBlock, circle)
    # (proposedBlock, broadcaster, signature, circle, randomHashes)

    convergenceHeader = approval['header']
    signatures = approval['signatures']
    broadcaster = approval['broadcaster']
    validInstruction = approval['validInstructions']
    circleAgents = approval['agentInfo']

    # GREG: Do in a Lucid Chart on how the circle converges
    # Setup the candidate structure and post to our convergenceProcessor to kick off the convergence process
    candidate = {}
    #
    candidate['blocksize'] = 0 #TODO
    candidate['blockHeader'] = {
        "version" : "entityVersionUsed", #TODO
        "staticHeight" : "height below which a fork is not allowed", #TODO
        "convergenceHeader" : convergenceHeader,
        "consensusCircle" : circleAgents,
        "blockSignatures" : signatures,
    }
    candidate["blockHash"] = encryptionUtilities.getHashofInput(candidate['blockHeader'])
    candidate["blockOriginatedAgent"] = broadcaster
    candidate["instructions"] = validInstructions

    logging.debug(f'candidate = {candidate}')

    # writing out a file doesnt work because in the rq worker container
    distributeBlock(candidate)

    return

def distributeBlock(block):
    #distribute across the network - write to redis for now

    red.sadd("candidateBlocks", block["blockHash"])
    red.append("candidateBlocks:" + block["blockHash"], json.dumps(block))

    # filePath = "candidates/" + block["blockHash"] + ".json"
    # blockFile = open(filePath, 'w')
    # blockFile.write(json.dumps(block))
    # blockFile.close()

# Distance calculations for finding the nearest agent to a number for a level. Uses Redis
# sorted set with lexographical ordering to find nearest (next largest) agent to the outputMatrix
# this may not be optimised
def nextCircle(searchTerms):
    circle, bIndex = [],0
    logging.debug(f'finding next circle with {searchTerms}')
    # Code this - SOLUTION: untrusted agents are removed from levels structure or given special untrusted level

    # TODO put exception handling around this
    # should return ["founders","defenders","protectors","contributors","members"]
    levels = list(red.zrange("levels", "0", "-1"))
    logging.debug(f'levels is {levels}')

    # for each level (in priority order search for agents)
    for level in levels:
        # TODO is there a better way to store the number of agents at a level
        # numAtLevel could eventually be adjusted to rather than bring in every agent
        # at that level before going to the next level (what happens now)
        # to bring in x agents from that level
        numAtLevel = int(red.hget("levelCount", level))
        # levelCount is the number of agents in the circle at that level
        levelCount = 0
        # copy the matrix into a search terms array this allows adjustment of the
        # matrix for when the search term should be a previously found agent instead of
        # the random number

        while (bIndex < len(searchTerms)) and levelCount < numAtLevel:
            # while you do not have too many agents and there are less agents then the
            # max number of agents wanted from this level (currently all the agents at the level)
            # then search for the next appropriate agent
            logging.debug(f'level count is {levelCount}, numAtLevel is {numAtLevel}')
            searchTerm = "(" + searchTerms[bIndex]
            logging.debug(f'searching for clostest num to {searchTerm}')
            logging.debug(f'possible agents are: {red.zrange(level, "0", "-1")}')
            nextAgent = red.zrangebylex(level, searchTerm, "+", start = 0, num = 1)
            logging.debug(f'level: {level}, nextAgent is {nextAgent}')

            # if next agent is [] then there is no agent after the search term in the
            # set and so we must loop around and grab the agent at the front
            if not nextAgent:
                logging.debug(f'no agent lets loop')
                nextAgent = red.zrange(level, "0", "0")
                if not nextAgent:
                    logging.debug(f' no agents at level {level}')
                    break

            nextAgent = ''.join(nextAgent)

            logging.debug(f'next agent is: {nextAgent}')
            logging.debug(f'number was {searchTerms[bIndex]}')
            if nextAgent in circle:
                # if the next agent after the random number is already in the circle
                # then we should find the next agent after this one this is achieved
                # by adjusting the search term from the random number to the agent already
                # in the circle, hence finding the next available agent after the random
                # number
                logging.debug(f"agent {nextAgent} was already in circle {circle}")
                searchTerms[bIndex] = nextAgent
                pass
            else:
                circle.append(nextAgent)
                bIndex = bIndex + 1
                levelCount += 1

    logging.debug(f'circle is {circle}')

    # Commented out.  manually adding the current agent if they didnt make the cut
    if not redisUtilities.getMyID() in circle:
        logging.info("my id not present removing so I am not in the circle ")
        #circle.pop()
        #circle.append(redisUtilities.getMyID())


    return circle
