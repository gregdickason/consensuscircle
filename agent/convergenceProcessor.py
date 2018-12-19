import requests
import json
from consensusEmulator import consensusEmulator
import redisUtilities
import blockUtilities
import agentUtilities

from redis import Redis
from rq import Queue

# This is the processor for converging the circle, it listens on a queue as convergence is asynchronous (non blocking).
# The agent does a full convergence as a single data packet with gossip protocol (see data structure as the reference)

# Test Initial implementation creates next block without convergence - signs off from all agents in circle

def generateNextCircle():

    # should always be the latest block that you are generating the next circle from
    nextCircle = redisUtilities.nextCircle(redisUtilities.getOutputMatrix(), [])  # No excluded agents for now

    # Am I in the circle?
    # TODO - check if in potentially a secondary circle.  If so start the convergence using this one in case primary fails
    if not (redisUtilities.getMyID() in nextCircle):
        # what should happen if not in next circle?
        # nothing - correct?

        return

    # Re-randomise the random hash we will use to converge (for each initiation of a block we are in):
    self.randomMatrix = [g for g in getRandomNumbers(32,5)]  # TODO - based on number in circle so need to use this parameter
    self.seed = getSeed(32)


    # gather and check instructions
    possibleInstructions = redisUtilities.getInstructionHashes()
    validInstructions = []
    for instructionHash in possibleInstructions:
        if blockUtilities.tryInstruction(instructionHash):
            validInstructions.append(agentUtilities.getDetailedInstruction(instructionHash))


    consensusEmulator.proposeInstructionSet(validInstructions, randomMatrix)

    # generate a candidate structure
    # Setup the candidate structure and post to our convergenceProcessor to kick off the convergence process
    candidate = {}

    candidate['blocksize'] = 0 #TODO
    candidate['blockHeader'] = {
        "version" : "entityVersionUsed", #TODO
        "staticHeight" : "height below which a fork is not allowed", #TODO
        "convergenceHeader" : {
            "previousBlock" : redisUtilities.getBlockHash(),
            "instructionsMerkleRoot" : agentUtilities.returnMerkleRoot(validInstructions),
            "instructionCount" : len(validInstructions),
            "blockHeight" : (redisUtilities.getBlockHeight() + 1),
            "randomNumbers" : getAgentsNumbers()
        },
        "consensusCircle" : #TODO,
        "blockSignatures" : ,
    }

     # TODO Use an orderedMap here for consistent Hash
     # myMap = {}
     # myMap["previousBlock"] = self.blockState.getBlockHash()
     # myMap["instructionsMerkleRoot"] = returnMerkleRoot(self.blockState.getInstructionHashes())
     # myMap["instructionCount"] = len(self.blockState.getInstructionList())
     # # TODO update instructionHandlers
     # # TODO fix as chain 0 isnt highest block?  Append issue?
     # myMap["blockHeight"] = (self.blockState.getBlockHeight() + 1) # 1 higher for next block
     # myMap["randomNumberHash"] = [g for g in hashvector(self.randomMatrix, self.seed)]
     # myGossip = {}
     # myGossip[self.agentID] = myMap
     # myGossip["sign"] = signMessage(myMap, self.agentPrivateKey)
     # myGossip["trusted"] = 1   # I trust myself
     # candidate["gossip"].append(myGossip)
     # candidate["broadcaster"] = self.agentID
     # candidate["signedGossip"] = signMessage(myGossip, self.agentPrivateKey)
     # candidate["instructionHashes"] = list(self.blockState.getInstructionHashes())
     # candidate["instructions"] = list(self.blockState.getInstructionList())

     # we send randomMatrix and seed too so this can be reused
     mySettings = {}
     mySettings["randomMatrix"] = list(self.randomMatrix)
     mySettings["seed"] = self.seed
     candidate["agentSettings"] = mySettings

     # post structure - do this through blockState
     blockUtilities.postJob(candidate)
     logging.debug(f'candidate = {candidate}')

    # CandidateStructure contains the candidate from our Agent or from ourselves based on previous call

    # For each input from other nodes in circle:
    # Parse their candidate and confirm valid, agree on trust, and remove instructions we have not in their candidate (if trusted) etc
    # Reform our candidate to conform, include who we trust.
    # Exit and wait for next round

    # If we dont need to reform as we are receiving what we have then REVEAL hashed numbers
    # wait for other reveals and confirm validity - propogate all reveals to everyone.  If no reveal from particular node in timeperiod, exclude and republish reveal without them
    # if all reveals line up with block, publish next block


    # Load config
    with open('agentConfig.json') as json_data:
      config = json.load(json_data)
      level = config['level']   # TODO this should be confirmed by the agent from the owners level (not independent).  In the blockState object
      agent_identifier = config['agentIdentifier']
      owner = config['ownerPublicKey']
      signedIdentifier = config['signedIdentifier']
      agentPrivKey = config['agentPrivateKey']

    # Now candidate structure is what we receive originally from the Agent and then from ourselves (we republish to the queue)  It is what we broadcast
    # Load candidate structure, then loop through all received candidates from other nodes and update - tracking if we needed to update


    # {'gossip': [{'17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920':
    #             {'previousBlock': '695E4A0C4F763FC95DFD6C29F334CC2EAF9C4A2BAFCCE09379B0864EDA001EB4',
    #             'instructionsMerkleRoot': 'c8fcdeb4fe643c368122da53c3ca92fd76634801d416ae68664bc13d16bd8b0b',
    #             'instructionCount': 1,
    #             'blockHeight': 0,
    #             'randomNumberHash': ['24f875bbde99270a3107f2983dc31195f0ef419bf83eeb1306aabf4a8e190ba6', 'a44d06440ac0cd6a1b24e4a4b224348493590d546cbdcad34f44449d51145a2b', '8277f91e9d59187edf78cf6d5c56cbc4118216ac0e6d998ba96f8618e25d051b', 'd650fc1d47c5d9ba80aa3a73d402bf8988da586a8c6d9728bd9ea221d299ad04', 'ad04a4676dd7bac39d5831a10b97870e81093e21dfb45a3b6e32548a327262b6']
    #             },
    #             'sign': 'bTDbEAU1R+Y2riI5QGZnU2QNroNgeLOl8UjrcxkM+8Y5pdovvETem9xuca3kFZ/oENJ97rL8EaqXEAuX1cYjwA==',
    #                'trusted': 1}
    #             ],
    #         'broadcaster': '17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920',
    #         'signedGossip': 'z9Ra2+sZqypR9Ev6iYn1l65Nhb6R/IRfT6h1wWTng4qeV6O6Oxc3XHmBNFLCxs9+JczQ28t9T4wjzk0XU8Oy0A==',
    #         'instructionHashes': ['5908a04a072f0beb2d7521bb9ec77662234c4a8ccb44d4e15541e91952380938'],
    #         'instructions': [{'source': '17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920', 'someRandom': 'e1148ec967f73d6ddaaf19c39c5ad8fab58ef8d7f430d5e36d653f9634f16633', 'slots': [{'wallet': 0, 'escrowAmount': 200000, 'action': 'update', 'somethingelse to work out': '', 'target': 'abs(vector1 + vector2) + AABB332D - uses consensus output as random seed (can be absolute)', 'timeout': 'timeInBlocksToAllow the next closest entity to update'}]}],
    #         'agentSettings': {'randomMatrix': ['731786ba2759286f2068c030a72de5ae5a11d3d8f0dd7d06d4a606eac6b80943', 'c2d36c11040e8f7085bc6dad1d0a53802c89ca0e4fd4aff49a55a773c3b716c3', '49ad5cf2bd108cd686f4f8f5d94c0ca8bc325fef946c5d194385e8e2d2daf7d5', 'ea48b75b62dc0c1ec5a8a8ab2379ccbe1f42d50266e929326a42e796db60efed', 'c9597ef7eae18437004d01288b2f51bb7cb4faa9e8ece755484efdfc16ebef09'],
    #         'seed': '2c917a7c9c79722822c482b809417606f7d73884dfd61828cabb8c33c34af2c1'}}

    candidateStructure = json.loads(candidateData)
    # TODO add in logging to this
    print(f'\nReceived {candidateStructure}')
    broadcaster = candidateStructure['broadcaster']
    print(f'\n\nAnd the broadcaster is {broadcaster}')

    # NORMALLY would now converge.  For this version we broadcast the block (publish it) as if convergence happened
    # sign from everyone
    candidateBlock = consensusEmulator(candidateStructure)



    # Step 1:  load the current blockstate from DB

    # Steps 2..n :

    # Post updated block to other

    return

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
