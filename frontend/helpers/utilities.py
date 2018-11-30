#!/usr/bin/python
import secrets
import hashlib
import socket
import argparse
import os

import logging.config

from ecdsa import SigningKey, VerifyingKey, NIST256p
from ecdsa.keys import BadSignatureError
from ecdsa.util import randrange_from_seed__trytryagain
from base64 import b64encode, b64decode
from collections import OrderedDict

ENCODING = 'utf-8'

# Get the hash for a json string (cast to str if not).
def getHashofInput(input):
  logging.debug(f'getHashofInput called with input {input}')
  inputNoWhitespace = ''.join(str(input).split())
  return hashlib.sha256(inputNoWhitespace.encode(ENCODING)).hexdigest()

# Cryptography section
# TODO:  Allow the agent and the participant to select their own cryptographic scheme for public / private keys (so the BlockChain supports any type of encryption
# including post quantum schemes.

# TODO use curve 25519 which is not from NIST and unlikely to have NSA backdoor?  ( https://github.com/warner/python-ed25519 ) - need local c compiler (get from https://ed25519.cr.yp.to/?)
# read https://security.stackexchange.com/questions/50878/ecdsa-vs-ecdh-vs-ed25519-vs-curve25519 for some context

# Stores the public key, signatures, etc in pure strings to enable appropriate JSON serialisation / deserialisation.  the "b'...'" format fails to deserialise
def binaryStringFormat(byte_content):
  logging.debug(f'binaryStringFormat called with byte_content {byte_content}')
  base64_bytes = b64encode(byte_content)
  return base64_bytes.decode(ENCODING)

def binFromString(myString):
  logging.debug(f'binFromString called with string {myString}')
  return b64decode(myString)

# Public / Private key cryptography
# Using https://github.com/warner/python-ecdsa for now.  NOTE: TIMING ATTACKS are possible so the agent can never solely sign a message in an external interface: need to mask somehow
# TODO: Need to manage process for signing in a way that timing attacks are not practical (no repeated calls allowed for example, no leakage of time in a circle process)
def signMessage(message, priKey):
  logging.debug(f'signMessage call with message {message} and key {priKey}')

  sk = SigningKey.from_pem(binFromString(priKey))   # TODO: should check this is properly pem encoded before processing
  # Using deterministic ecdsa signature to prevent possible leakage through non randomness.  See https://tools.ietf.org/html/rfc6979
  return binaryStringFormat(sk.sign_deterministic(str(message).encode(ENCODING),hashlib.sha256))

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=6000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # The app is running on open port.  Dont include the 0.0.0.0 if concerned about external access
    app.run(host='0.0.0.0', port=port)
