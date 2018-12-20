import requests
import json
import consensusEmulator
import redisUtilities
import blockUtilities
import agentUtilities
import logging.config

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
def distributeBlock(block):
    #distribute across the network - write to redis for now

    red.sadd("candidateBlocks", block["blockHash"])
    red.sadd("candidateBlocks:" + block["blockHash"], json.dumps(block))

    filePath = "candidates/" + block["blockHash"] + ".json"
    blockFile = open(filePath, 'w')
    blockFile.write(json.dumps(block))
    blockFile.close()

# Distance calculations for finding the nearest agent to a number for a level.  This is not optimised as will be in a data structure in Lambda
# currently it is order of N which will get very big.  Needs to be rewritten with binHashTree (TODO)
# Note this is in memory for the test version that this blockstate manages.  Different implementation in cloud versions
def nextCircle(self,lastBlockMatrix, excludedAgents):
    nextCircle, bIndex = [],0
    logging.debug(f'in next circle with lastBlockMatrix: {lastBlockMatrix}, excludedAgents: {excludedAgents}')
    # Code this - SOLUTION: untrusted agents are removed from levels structure or given special untrusted level
    levels = list(self.red.smembers("levels"))
    logging.debug(f'levels is {levels}')

    # find next agent and delete from level so cant be chosen twice:
    for level in levels:
        possibleAgents = list(self.red.smembers(level))
        logging.debug(f'possibleAgents is {possibleAgents}')
        # may want to optimise this sort
        possibleAgents.sort() #taken from the old sorting on initialisation
        while possibleAgents and (bIndex < len(lastBlockMatrix)):
            nextAgent = self.takeClosest(possibleAgents, lastBlockMatrix[bIndex])
            logging.debug(f'next agent is: {nextAgent}')
            possibleAgents.remove(nextAgent)
            nextCircle.append(nextAgent)
            bIndex = bIndex + 1

    logging.debug(f'nextCircle is {nextCircle}')
    return nextCircle


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

def generateNextCircle():

    print("generating the next circle")

    # should always be the latest block that you are generating the next circle from
    nextCircle = nextCircle(redisUtilities.getOutputMatrix(), [])  # No excluded agents for now

    # Am I in the circle?
    # TODO - check if in potentially a secondary circle.  If so start the convergence using this one in case primary fails
    if not (redisUtilities.getMyID() in nextCircle):
        # what should happen if not in next circle?
        # nothing - correct?

        return

    # Re-randomise the random hash we will use to converge (for each initiation of a block we are in):
    randomMatrix = [g for g in getRandomNumbers(32,5)]  # TODO - based on number in circle so need to use this parameter
    seed = getSeed(32)

    # gather and check instructions
    possibleInstructions = redisUtilities.getInstructionHashes()
    validInstructions = []
    for instructionHash in possibleInstructions:
        if blockUtilities.tryInstruction(instructionHash):
            validInstructions.append(agentUtilities.getDetailedInstruction(instructionHash))


    proposedBlock = {
        "previousBlock" : redisUtilities.getBlockHash(),
        "instructionsMerkleRoot" : agentUtilities.returnMerkleRoot(validInstructions),
        "instructionCount" : len(validInstructions),
        "blockHeight" : (redisUtilities.getBlockHeight() + 1),
        "instructions" : json.dumps(validInstructions),
        "broadcaster" : agentUtilities.getMyID()
    }

    approval = consensusEmulator.proposeConvergenceHeader(proposedBlock, randomMatrix, nextCircle)

    convergenceHeader = approval['header']
    signatures = approval['signatures']
    broadcaster = approval['broadcaster']
    validInstruction = approval['instructions']
    randomNumbers = approval["randomNumbers"]

    # generate a candidate structure
    # Setup the candidate structure and post to our convergenceProcessor to kick off the convergence process
    candidate = {}
    #
    candidate['blocksize'] = 0 #TODO
    candidate['blockHeader'] = {
        "version" : "entityVersionUsed", #TODO
        "staticHeight" : "height below which a fork is not allowed", #TODO
        "convergenceHeader" : convergenceHeader,
        "consensusCircle" : nextCircle,
        "blockSignatures" : signatures,
    }
    candidate["blockHash"] = agentUtilities.getHashofInput(candidate['blockHeader'])
    candidate["blockOriginatedAgent"] = broadcaster
    candidate["instructions"] = validInstructions

    logging.debug(f'candidate = {candidate}')

    # writing out a file doesnt work because in the rq worker container
    distributeBlock(candidate)

    return
