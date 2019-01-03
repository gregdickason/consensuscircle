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

    print("generating the next circle")

    # should always be the latest block that you are generating the next circle from
    circle = nextCircle(redisUtilities.getOutputMatrix())  # No excluded agents for now

    # Am I in the circle?
    # TODO - check if in potentially a secondary circle.  If so start the convergence using this one in case primary fails
    if not (redisUtilities.getMyID() in circle):
        # what should happen if not in next circle?
        # nothing - correct?
        logging.info("I AM NOT IN THE NEXT CIRCLE")

        return

    # gather and check instructions
    possibleInstructions = redisUtilities.getInstructionHashes()
    validInstructions = []
    validInstructionHashes = []
    for instructionHash in possibleInstructions:
        if blockUtilities.tryInstruction(instructionHash):
            logging.debug('instruction was valid')
            validInstructionHashes.append(instructionHash)
            validInstructions.append(redisUtilities.getInstruction(instructionHash))

    logging.debug(f'valid instructions is: {validInstructions}')
    if len(validInstructions) == 0:
        logging.info("there are no valid instructions and so, no valid block")
        return

    proposedBlock = {
        "previousBlock" : redisUtilities.getBlockHash(),
        "instructionsMerkleRoot" : encryptionUtilities.returnMerkleRoot(validInstructionHashes),
        "instructionCount" : len(validInstructions),
        "blockHeight" : (redisUtilities.getBlockHeight() + 1),
        "instructions" : json.dumps(validInstructions),
        "broadcaster" : redisUtilities.getMyID()
    }

    approval = consensusEmulator.proposeConvergenceHeader(proposedBlock, circle)
    # (proposedBlock, broadcaster, signature, circle, randomHashes)

    convergenceHeader = approval['header']
    signatures = approval['signatures']
    broadcaster = approval['broadcaster']
    validInstruction = approval['validInstructions']
    circleAgents = approval['agentInfo']

    # generate a candidate structure
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

# Distance calculations for finding the nearest agent to a number for a level.  This is not optimised as will be in a data structure in Lambda
# currently it is order of N which will get very big.  Needs to be rewritten with binHashTree (TODO)
# Note this is in memory for the test version that this blockstate manages.  Different implementation in cloud versions
def nextCircle(lastBlockMatrix):
    circle, bIndex = [],0
    logging.debug(f'in next circle with lastBlockMatrix: {lastBlockMatrix}')
    # Code this - SOLUTION: untrusted agents are removed from levels structure or given special untrusted level
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
        searchTerms = lastBlockMatrix

        while (bIndex < len(lastBlockMatrix)) and levelCount < numAtLevel:
            # while you do not have too many agents and there are less agents then the
            # max number of agents wanted from this level (currently all the agents at the level)
            # then search for the next appropriate agent
            logging.debug(f'level count is {levelCount}, numAtLevel is {numAtLevel}')
            searchTerm = "(" + searchTerms[bIndex]
            logging.debug(f'searching for clostest num to {searchTerm}')
            logging.debug(f'possible agents are: {red.zrange(level, "0", "-1")}')
            nextAgent = red.zrangebylex(level, searchTerm, "[\xff", start = 0, num = 1)
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
            logging.debug(f'number was {lastBlockMatrix[bIndex]}')
            if nextAgent in circle:
                # if the next agent after the random number is already in the circle
                # then we should find the next agent after this one this is achieved
                # by adjusting the search term from the random number to the agent already
                # in the circle, hence finding the next available agent after the random
                # number
                logging.debug(f"agent {nextAgent} was already in circle {circle}")
                searchTerms[bIndex] = nextAgent
            else:
                circle.append(nextAgent)
                bIndex = bIndex + 1
                levelCount += 1

    logging.debug(f'circle is {circle}')

    # manually adding the current agent if they didnt make the cut
    if not redisUtilities.getMyID() in circle:
        logging.info("my id not present removing so I can add")
        circle.pop()
        circle.append(redisUtilities.getMyID())


    return circle
