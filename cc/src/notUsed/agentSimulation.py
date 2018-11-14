#!/usr/bin/python
import secrets
import hashlib
import socket
import argparse


# This contains definitions that are used for convergence, management of the circle, etc

# It also demonstrates how a random number is created in a matrix composed of vectors from 5 agents in a consensus circle
# And implements the final stage of the convergence protocol as part of consensus circle
# Assumption of no cheating in this version, but cheating checks will be instituted in later versions

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






# Code to test
# Take in output into a vector and can then use this output to merge next vector
# using secrets module:  https://docs.python.org/3/library/secrets.html#module-secrets
# note we are working on 2 byte numbers (2^16) = 65536 as maximum, so we modulus on this
# in actual consensus circle will use 256 bit (32 byte) numbers.  


# connect to peers - use a file as input for who to connect to (in real world will be blockchain itself)
# peerfiles

# I am slot 1 in my world so create my slot with random numbers:
slot1 = [int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16)]
print("My Random Numbers are: ", slot1)

# create a seed to hash with - will broadcast the seed on the reveal
seed = int(secrets.token_hex(2),16)
hashv = [ g for g in hashvector(slot1,seed)]
print("My hashed random numbers are: " , hashv)
print("My seed is: " , seed)


#broadcast my hashes to other nodes


#Take in other nodes hashes 


#when have all hashes - broadcast my actual numbers and seeds 
# TODO: other nodes hashes.  For now we are creating them ourselves
slot2 = [int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16)]
print(slot2)
slot3 = [int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16)]
print(slot3)
slot4 = [int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16)]
print(slot4)
slot5 = [int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16),int(secrets.token_hex(2),16)]
print(slot5)


# Create matrix from the vectors received.  Note that would need to check lengths in production - assumption is each vector same length
mat = [slot1,slot2,slot3,slot4,slot5]

# output     

print("\nOutput from converging above at modulus of 2 byte numbers:\n",[g for g in converge(mat,2**16)])

