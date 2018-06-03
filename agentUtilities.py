#!/usr/bin/python
import secrets
import hashlib
import socket
import argparse


# Stateless Utility Functions. Also used to translate between blockchain native formats and cryptographic representations.  So if move from sha256 to a 
# quantum computer resistant cryptographic function, all changes will be here

# Define how to converge matrices with modulus (a) as input to the function. 
# We receive the matrices as hex values 
def converge(m,a):
  rlen, clen, i, j, s = len(m[0]), len(m), 0, 0, 0
  while i < rlen:
    while j < clen:
      s = (s+int(m[j][i],16))%a
      j += 1
    yield(format(s,'x'))
    s, j = 0, 0
    i += 1


# calculate the block distance for the most recent block vs the one before - used to keep the Depth weighted chain distances to choose which blockchain to follow

# we always hash with a seed of same size as the input to prevent peer agents knowing our hash (assuming they have precalculated)
# so take in vector and seed and output hashes
def hashvector(v,s):
  vlen, i, out = len(v), 0, []
  while i < vlen:
    yield hashlib.sha256(str(v[i]).encode('utf-8') + str(s).encode('utf-8')).hexdigest()
    i += 1



# Get the hash for a json string.
def getHashofInput(input):
  inputNoWhitespace = ''.join(input.split())
  return hashlib.sha256(inputNoWhitespace.encode('utf-8')).hexdigest()
  
def getRandomNumbers(byteLen, numberEntries):
  for x in range(0,numberEntries):
    yield(secrets.token_hex(byteLen))
   
def getRandomNumber(byteLen):
  number = secrets.token_hex(byteLen)  
  return number
   
def getSeed(byteLen):
  seed = secrets.token_hex(byteLen) # this comes back as decimal on the return for some reason.  TODO confirm the return and use
  return seed
  
def returnCircleDistance(lastBlockRandomMatrix, consensusCircle, numInstructions, circleEntityInstructionNumber):
  # Calculates the mean distance of the current consensusCircle to the lastBlockRandomMatrix (equation per whitepaper)
  # TODO check if better to have less nodes.  --> only likely if agent is further away than 1/17 of the size of sha256
  
  # First check consensusCircle length is less than or equal to lastBlockRandomMatrix length (can be less if no nodes present)
  lbLen, ccLen, i, sum = len(lastBlockRandomMatrix), len(consensusCircle), 0, 0
  assert ccLen <= lbLen
  
  while i < ccLen:
    sum = sum + returnHashDistance(lastBlockRandomMatrix[i], consensusCircle[i])
    i += 1
  
  return (sum /(ccLen/lbLen))*(circleEntityInstructionNumber/numInstructions)
  
def checkBlock(blockHash):
  # Utility function to check if the block has already been processed and is in the chain or a discarded chain. return True for now
  return True 

# TODO - put in --> def returnDepthWeightedChainDistance which weights chain by CircleDistances  (using the chain structure we are tracking).  
# maybe we tie off at a depth of 100 so that the blocks dont need to go back to genesis?
  
def returnHashDistance(blockHash, agentIdentifier):
  # Returns the integer distance between 2 32 byte hashes (base16 input).  TODO - Replace with function that returns which is larger to allow any type of comp
  return abs(int(blockHash,16) - int(agentIdentifier,16))  