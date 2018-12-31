
import encryptionUtilities
import redisUtilities
import json


# Class that emulates a consensus circle.  Loads the 5 private keys from the circle and
# creates a block from a candidateBlock
# Only used for testing

agentPriKeys = {
    "180cedac0f95b45ec18cdcd473d14d44b512ef16fc065e6c75c769b544d06675" : "f97dcf17b6d0e9f105b6466b377024a9557a7745a9d7ba7dc359aeeeb4530a9e",
    "2efb6ec38d1f9ccfa4b1b88bd98ab9b09c4a484496a5713af177b971ccfb922b" : "e53ab4e385290bf0e24982fd40bb4f626985f75f6c84db6fa46d75ae9da886aa",
    "2c24af4bd0889b10e325733c9b468779db7b2a82e9052df3b46a8aa1078262ea" : "b07e2f91e2702f194931eb99d889114b09dfd35d9f6f2fd04d6fdf82d44c5a7a",
    "031a3a259e059ec67971841a267528af2fc42bfcc1271259164b822fedf86102" : "430b7686d4dece852e8d28ddd82698bcd0db00bb986bfba71eb9b0288e09f467",
    "5aebce47cab0ff962b7bfde34949f557e5826ccf0a8a572e2f8c8769deb8e58b" : "3582e8f1f33fdfab3c927e6daeb2faf41d9383d078af720fcd93fc4afd7c37c7",
    "6c2add4237bd9ae4917edbbfc51277816196101affc79b46dc574c7b86df4ef9" : "0463d5d93475e4ed4538febd0d547dd32dee16e8a5d9d257c8eb132dd29d26f0",
    "97c4d1d971056016b841dfdfb759aa606d47d6b1d01af5d6b2552505c464f620" : "b5cf01dd19b17a2eb7b7fea1a254f47e286927942fb532388922e4368ea33786",
    "7a319d90121a0113df0333fdf8f4633167f23c398987391a0bbea55b1676ca4f" : "abb24ffd54466787a97238aa265fc3b68ce3b43f302445efd7f3c424ded9068e",
    "359c45d4cb0606f903249bea19da3c178940e2633f34f55c9dca4e425696c1a0" : "8d25f09d66ef3cb3336355944e8015c6544b6b7fc4b7fa9ed5289718f91c9448"
}

def proposeConvergenceHeader(proposedInstructions, randomMatrix, circle):

    response = {}
    response["header"] = {
           "previousBlock" : proposedInstructions["previousBlock"],
           "instructionsMerkleRoot" : proposedInstructions["instructionsMerkleRoot"],
           "instructionCount" : proposedInstructions["instructionCount"],
           "blockHeight" : proposedInstructions["blockHeight"],
           "randomNumbers" : getRandomNumbers(circle)
    }
    response["signatures"] = getSignatures(response["header"], circle)
    response["agentInfo"] = getAgentInfo(circle)
    response["broadcaster"] = proposedInstructions["broadcaster"]
    response["validInstructions"] = proposedInstructions["instructions"]

    return response

# inefficient loops circle 3x
def getAgentInfo(circle):

    agentInfo = []
    for agent in circle:
        level = redisUtilities.getLevel(agent)
        agentInfo.append({"level" : level, "agentID" : agent})

    return agentInfo

def getRandomNumbers(circle):
    randomNumbers = []

    for agent in circle:
        randomMatrix = [g for g in encryptionUtilities.getRandomNumbers(32,len(circle))]  # TODO - based on number in circle so need to use this parameter
        randomNumbers.append({agent : randomMatrix})

    return randomNumbers

def getSignatures(message, circle):
    signatures = []

    hashMessage = encryptionUtilities.getHashofInput(message)

    for agent in circle:
        signatures.append({agent : encryptionUtilities.signMessage(hashMessage, agentPriKeys[agent])})

    return signatures
