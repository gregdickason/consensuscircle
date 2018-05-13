#!/usr/bin/python
import secrets
import hashlib
import socket
import argparse


# This contains definitions that are used for convergence, management of the circle, etc
# Also contains helper classes for managing convergence routines, gossip protocols, managing different node distances, etc


# Define how to converge matrices with modulus (a) as input to the function. 
def converge(m,a):
  rlen, clen, i, j, s = len(m[0]), len(m), 0, 0, 0
  while i < rlen:
    while j < clen:
      s = (s+m[j][i])%a
      j += 1
    yield(s)
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

  
def getRandomNumbers(byteLen, numberEntries):
  for x in range(0,numberEntries):
    yield(secrets.token_hex(byteLen))
   
def getRandomNumber(byteLen):
  number = secrets.token_hex(byteLen)  
  return number
   
def getSeed(byteLen):
  seed = secrets.token_hex(byteLen) # this comes back as decimal on the return for some reason.  TODO confirm the return and use
  return seed
  
  
def returnHashDistance(blockHash, agentIdentifier):
  # This is the routine that confirms if the agentIdentifier should be in the block.  If returns a blockDistance object that includes the lowest known agents (block membership is probabilistic)
  # In production we will rely on database mechanisms  For now we parse the current known agents
  print(f'Got {blockHash} as blockhash and {agentIdentifier}')
  # Absolute value of the subtraction between the 2:
  return abs(int(blockHash,16) - int(agentIdentifier,16))  