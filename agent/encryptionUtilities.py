#!/usr/bin/python
import secrets
import hashlib
import socket
import argparse
import os
import re

import logging.config

import ecdsa
from ecdsa import SigningKey, VerifyingKey, NIST256p
from ecdsa.keys import BadSignatureError
from ecdsa.util import randrange_from_seed__trytryagain
from base64 import b64encode, b64decode
from collections import OrderedDict
import json

ENCODING = 'utf-8'

# Stateless Utility Functions. Also used to translate between blockchain native formats and cryptographic representations.  So if move from sha256 to a
# quantum computer resistant cryptographic function, all changes will be here

# Define how to converge matrices with modulus (a) as input to the function.
# We receive the matrices as hex values
def converge(m,a):
  logging.debug(f'converge called with m {m}, a {a}')
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
  logging.debug(f'hashvector called with v {v}, s {s}')
  vlen, i, out = len(v), 0, []
  while i < vlen:
    yield getHashofInput(v[i] + s)
    i += 1

def getHashWithSeed(input,seed):
  logging.debug(f'getHashWithSeed called with inut {input}, seed {seed}')
  input = json.dumps(input)
  pattern = re.compile(r'\s+')
  inputNoWhitespace = re.sub(pattern, '', input)
  return hashlib.sha256(inputNoWhitespace.encode(ENCODING) + seed.encode(ENCODING)).hexdigest()


# Get the hash for a json string (cast to str if not).
def getHashofInput(input):

    input = json.dumps(input)
    pattern = re.compile(r'\s+')
    inputNoWhitespace = re.sub(pattern, '', input)
    logging.debug(f'getHashofInput called with input {inputNoWhitespace}')
    return hashlib.sha256(inputNoWhitespace.encode(ENCODING)).hexdigest()

def getRandomNumbers(byteLen, numberEntries):
  logging.debug(f'getRandomNumbers called with byteLen {byteLen}, numberEntries {numberEntries}')
  for x in range(0,numberEntries):
    yield(secrets.token_hex(byteLen))

def getRandomNumber(byteLen):
  logging.debug(f'getRandomNumber called with byteLen {byteLen}')
  number = secrets.token_hex(byteLen)
  return number

def getSeed(byteLen):
  logging.debug(f'getSeed called with byteLen {byteLen}')
  seed = secrets.token_hex(byteLen)
  return seed

def returnCircleDistance(lastBlockRandomMatrix, consensusCircle, numInstructions, circleEntityInstructionNumber):
  logging.debug(f'returnCircleDistance called with lastBlockRandomMatrix {lastBlockRandomMatrix}, consensusCircle {consensusCircle}, \
    numInstructions {numInstructions}, circleEntityInstructionNumber {circleEntityInstructionNumber}')
  # Calculates the mean distance of the current consensusCircle to the lastBlockRandomMatrix (equation per whitepaper)
  # TODO check if better to have less nodes (lower circle distance).  --> only likely if agent is further away than 1/17 of the size of sha256
  # First check consensusCircle length is less than or equal to lastBlockRandomMatrix length (can be less if some agents not present)
  lbLen, ccLen, i, sum = len(lastBlockRandomMatrix), len(consensusCircle), 0, 0

  logging.debug(f'len of lastBlockRandomMatrix us {lbLen}')
  logging.debug(f'len of lastBlockRandomMatrix us {ccLen}')
  logging.debug(f'lastBlockRandomMatrix us {lastBlockRandomMatrix}')
  logging.debug(f'len of lastBlockRandomMatrix us {consensusCircle}')


  # TODO if there is a missing cc it might not be the end, so need to remove the lastBlock element that did not have a claimed CC member BEFORE this routine
  assert ccLen == lbLen  # need to handle assert in the calling code as exception

  while i < ccLen:
    sum = sum + returnHashDistance(lastBlockRandomMatrix[i], consensusCircle[i])
    i += 1

  # Now have to handle approximation issues between binary and non binary representations of numbers and the impact on computer floating point arithmetic -
  # normally accurate to 53 bits, we do this by rounding the factors by squaring the lbLen.
  # Floating point arithmetic limits us to approx 56 significant bits
  # TODO update whitepaper for definition including the rounding factor (makes a multiple of 1,2,3 etc)
  roundInsCountTarget = round(circleEntityInstructionNumber/numInstructions)
  if roundInsCountTarget == 0:
    roundInsCountTarget = 1

  chainRatio = round(lbLen**2 / ccLen)  # approxately a factor of 1/circleNumber of the 2**64 space per agent that drops out)

  return format(int(sum * chainRatio *roundInsCountTarget),'64x')


# TODO - put in --> def returnDepthWeightedChainDistance which weights chain by CircleDistances  (using the chain structure we are tracking).
# maybe we tie off at a depth of 100 so that the blocks dont need to go back to genesis?

def returnHashDistance(blockHash, agentIdentifier):
  logging.debug(f'returnHashDistance called with blockHash {blockHash}, agentIdentifier {agentIdentifier}')
  # Returns the integer distance between 2 32 byte hashes (base16 input).  TODO - Replace with function that returns which is larger to allow any type of comp
  return abs(int(blockHash,16) - int(agentIdentifier,16))


# Cryptography section
# TODO:  Allow the agent and the participant to select their own cryptographic scheme for public / private keys (so the BlockChain supports any type of encryption
# including post quantum schemes.

# TODO use curve 25519 which is not from NIST and unlikely to have NSA backdoor?  ( https://github.com/warner/python-ed25519 ) - need local c compiler (get from https://ed25519.cr.yp.to/?)
# read https://security.stackexchange.com/questions/50878/ecdsa-vs-ecdh-vs-ed25519-vs-curve25519 for some context

# Public / Private key cryptography - HEX EDIT
# Using https://github.com/warner/python-ecdsa for now.  NOTE: TIMING ATTACKS are possible so the agent can never solely sign a message in an external interface: need to mask somehow
# TODO: Need to manage process for signing in a way that timing attacks are not practical (no repeated calls allowed for example, no leakage of time in a circle process)
def signMessage(message, privateKey):
  logging.debug(f'signMessage call with message {message} and key {privateKey}')

  sk = SigningKey.from_string(bytes.fromhex(privateKey), curve = NIST256p)   # TODO: should check this is properly pem encoded before processing
  # Using deterministic ecdsa signature to prevent possible leakage through non randomness.  See https://tools.ietf.org/html/rfc6979
  return sk.sign_deterministic(str(message).encode(ENCODING), hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der).hex()

def verifyMessage(message, signedMessage, publicKey):
  logging.debug(f'verifyMessage call with message {message}, signedMessage {signedMessage} and key {publicKey}')

  publicKey = re.sub('^04', '', publicKey)

  # Log entry
  vk = VerifyingKey.from_string(bytes.fromhex(publicKey), curve = NIST256p)
  try:
    return vk.verify(bytes.fromhex(signedMessage),str(message).encode(ENCODING),hashfunc=hashlib.sha256, sigdecode=ecdsa.util.sigdecode_der)
  except BadSignatureError:
    # Log bad signature.  TODO import bad signature error
    return False
  return False

def signMessageFromPassPhrase(message, passphrase):
  logging.debug(f'signMessageFromPassPhrase call with message {message} and passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  return signMessage(message,sk.to_string().hex())

def verifyMessageFromPassPhrase(message, signedMessage, passphrase):
  logging.debug(f'verifyMessageFromPassPhrase call with message {message}, signedMessage {signedMessage} and passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  vk = sk.get_verifying_key()
  return verifyMessage(message,signedMessage,vk.to_string().hex())

def getPublicKeyFromPassPhrase(passphrase):
  logging.debug(f'getPublicKeyFromPassPhrase called with passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  vk = sk.get_verifying_key()
  return '04' + vk.to_string().hex()

def getPrivateKeyFromPassPhrase(passphrase):
  logging.debug(f'getPrivateKeyFromPassPhrase called with passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  return sk.to_string().hex()


# Diffie - Hellman.  Using ecdsa BUT not the private key of the current agent as want perfect forward secrecy.  We therefore trade a
# new session key based on a random variable.
# default is perfect forward secrecy: we generate a session key everytime we interact.  This means agents do not store private keys in long
# term storage
def createSessionKeyFromPublicKey(publicKey):
  logging.debug(f'createSessionKeyFromPublicKey called with pubKey {publicKey}')
  # Random Number:
  mySecret = os.urandom()

#def encryptWithSessionKey(sessKey):


#def decryptWithSessionKey(sessKey):

### Merkle Tree Routines.  Borrowing from https://github.com/JaeDukSeo/Simple-Merkle-Tree-in-Python/blob/master/MerkleTrees.py but
## using ordered Merkle Trees as the order of processing instructions in a block is based on the hash of instructions / instruction handlers
def returnMerkleRoot(myUnorderedArray):
  logging.debug(f'returnMerkleRoot called with array {myUnorderedArray}')

  # TODO confirm how to raise exceptions with logging.error or raising regular exceptions
  if len(myUnorderedArray) == 0:
    # raise Exception('an empty array was passed to returnMerkleRoot')
  # TODO remove next line - hardcoded to make work and then uncomment/replace exception above
    return getHashofInput('abc')

  # first hash and sort the array
  myList = [getHashofInput(x) for x in myUnorderedArray]
  # bubble sort - this is highly optimised in C code
  myList.sort()

  # We have a temporary list that replaces myList each loop
  while len(myList) > 1:
    tempList = []
    for i in range(0,len(myList),2):
      current = myList[i]
      if i + 1 != len(myList):
        currentRight = myList[i+1]
      else:
        currentRight=''
      tempList.append(getHashofInput(current + currentRight))
    myList = tempList[:]
  return myList[0]
