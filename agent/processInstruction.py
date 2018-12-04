import json
import logging.config

#utility functions for processing instructions - pool is run by the agent
from agentUtilities import getHashofInput, verifyMessage

# validate Instruction: confirm hash values and signature.  Does not add to pool or update any temp status (done in processInstruction)
def validateInstruction(instruction, blockState):
  returnValue = {
        'message': f'Instruction Accepted',
        'return': True
    }

  body = instruction['instruction']
  hash = instruction['instructionHash']
  sign = instruction['signature']
  sender = body['sender']

  if getHashofInput(body) != hash:
    logging.info(f'hash of instruction does not match: {getHashofInput(body)}')
    returnValue['message'] = f'Incorrect hash for Instruction at {hash}'
    returnValue['return'] = False
    return returnValue

  publicKey = blockState.getPublicKey(sender)

  logging.debug(f'publicKey is {publicKey}')

  # if getPubKey of sender is None, we dont know the sender (not on chain).  We deny them
  if publicKey == None:
    logging.info(f'Sender not known, reject')
    returnValue['message'] = f'Public Key of sender not registered on chain'
    returnValue['return'] = False
    return returnValue

  # TODO confirm signature - if this is false then reject (sohuld we untrust sender?)
  if verifyMessage(hash, sign, publicKey) != True:
    logging.info(f'Instruction for {hash} not verified - signature {sign} for {pKey} pkey incorrect')
    returnValue['message'] = f'Signature does not match'
    returnValue['return'] = False

  return returnValue

# validate Instruction: confirm hash values and signature.  Does not add to pool or update any temp status (done in processInstruction)
def validateInstructionHandler(instructionHandler):
  returnValue = {
          'message': f'InstructionHandler Accepted',
          'return': True
      }

  required = ['instructionHandlerHash', 'sign', 'instructionHandler']
  if not all(k in instructionHandler for k in required):
    returnValue['message'] = f'InstructionHandler for {hash} not well formed'
    returnValue['return'] = False
    return returnValue

  body = instructionHandler['instructionHandler']
  hash = instructionHandler['instructionHandlerHash']
  sign = instructionHandler['sign']

  if getHashofInput(body) != hash:
    returnValue['message'] = f'Incorrect hash for InstructionHandler at {hash}'
    returnValue['return'] = False
    return returnValue

  # TODO confirm signature


  return returnValue
