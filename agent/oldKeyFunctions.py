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

ENCODING = 'utf-8'

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

def verifyMessage(message, signedMessage, pubKey):
  logging.debug(f'verifyMessage call with message {message}, signedMessage {signedMessage} and key {pubKey}')
  # signed message is b64 encoded.  We decode
  # Log entry
  vk = VerifyingKey.from_pem(binFromString(pubKey))
  try:
    return vk.verify(binFromString(signedMessage),str(message).encode(ENCODING),hashlib.sha256)
  except BadSignatureError:
    # Log bad signature.  TODO import bad signature error
    return False
  return False

def signMessageFromPassPhrase(message, passphrase):
  logging.debug(f'signMessageFromPassPhrase call with message {message} and passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  return signMessage(message,binaryStringFormat(sk.to_pem()))

def verifyMessageFromPassPhrase(message, signedMessage, passphrase):
  logging.debug(f'verifyMessageFromPassPhrase call with message {message}, signedMessage {signedMessage} and passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  vk = sk.get_verifying_key()
  return verifyMessage(message,signedMessage,binaryStringFormat(vk.to_pem()))


def getPublicKeyFromPassPhrase(passphrase):
  logging.debug(f'getPublicKeyFromPassPhrase called with passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  vk = sk.get_verifying_key()
  return binaryStringFormat(vk.to_pem())

def getPrivateKeyFromPassPhrase(passphrase):
  logging.debug(f'getPrivateKeyFromPassPhrase called with passphrase {passphrase}')
  secexp = randrange_from_seed__trytryagain(hashlib.sha256(str(passphrase).encode(ENCODING)).hexdigest(), NIST256p.order)
  sk = SigningKey.from_secret_exponent(secexp, curve=NIST256p)
  return binaryStringFormat(sk.to_pem())

print('agent signing agent id')
print(signMessage('17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920', 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSVBsOXp4ZTIwT254QmJaR2F6ZHdKS2xWZW5kRnFkZTZmY05acnU2MFV3cWVvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFcmw2ZnVrQnVKU241ZWZ2N21Mei90Y09RaGsrTXRTU0JZYnorNHBheWdueGo4MlQzZ0VZOQpsU1pseUtpUzdDVnd6QmF2WHpDZmpxeGtaa09hazZoR2J3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo='))
print('owner signing agent id')
print(signMessage('17120c812977a00d3607375ff4e9c74be9f58dfe31f110ecf20ff957582fc920', 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUoyeGpwUTVadEJMSVVDTDNqRXA2U2JwU0dUQzlnMmk1YWJRNjgwK1ZIT0lvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFbU5FZVpEOWk1SW1iUUE0MFRHQjdZTHVqdjM2K1g3OUpRcWFJV2RsRVp6M3FQeXpVYnRmdgpaQ24xSG5wUGJuVW1Kc3hQa1gxaWZ0bUFZTytUaEFqMHpRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo='))
