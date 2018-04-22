#!/usr/bin/python
import secrets
import hashlib
import socket
import argparse


# This contains definitions that are used for convergence, management of the circle, etc

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

# we always hash with a seed of same size as the input to prevent peer agents knowing our hash (assuming they have precalculated)
# so take in vector and seed and output hashes
def hashvector(v,s):
  vlen, i, out = len(v), 0, []
  while i < vlen:
    yield hashlib.sha256(str(v[i]).encode('utf-8') + str(s).encode('utf-8')).hexdigest()
    i += 1


def getRandomNumbers(byteLen, numberEntries):
  for x in range(0,numberEntries):
    yield(int(secrets.token_hex(byteLen),16))
   
   
def getSeed(byteLen):
  seed = int(secrets.token_hex(byteLen),16)  
  return seed