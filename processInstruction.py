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
    
  required = ['instructionHash', 'sign', 'instruction']
  if not all(k in instruction for k in required):
    logging.info(f'Not all instruction required fields present')
    returnValue['message'] = f'Instruction  not well formed'
    returnValue['return'] = False
    return returnValue
  
  body = instruction['instruction']
  hash = instruction['instructionHash']
  sign = instruction['sign']
  sender = body['source']
    
  if getHashofInput(body) != hash:
    logging.info(f'hash of instruction does not match: {getHashofInput(body)}')  
    returnValue['message'] = f'Incorrect hash for Instruction at {hash}'
    returnValue['return'] = False
    return returnValue
    
  pKey = blockState.getPubKey(sender)
  
  
  logging.debug(f'pKey is {pKey}')
  
  # if getPubKey of sender is None, we dont know the sender (not on chain).  We deny them
  if pKey == None:
    logging.info(f'Sender not known, reject')
    returnValue['message'] = f'Public Key of sender not registered on chain'
    returnValue['return'] = False
    return returnValue
  
  # TODO confirm signature - if this is false then reject (sohuld we untrust sender?)
  if verifyMessage(hash, sign, pKey) != True:
    logging.info(f'Instruction not verified - signature incorrect')
    returnValue['message'] = f'Signature does not match'
    returnValue['return'] = False
  
  
  return returnValue
  
# validate Instruction: confirm hash values and signature.  Does not add to pool or update any temp status (done in processInstruction)
def validateInstructionHandler(instructionHandler):
  body = instructionHandler['instructionHandler']
  hash = instructionHandler['instructionHandlerHash']
  sign = instructionHandler['sign']
  
  returnValue = {
          'message': f'InstructionHandler Accepted',
          'return': True
      }
  
  # TODO check if we need this for performance (seems to add 400ms)
  required = ['instructionHandlerHash', 'sign', 'instructionHandler']
  if not all(k in instructionHandler for k in required):
    returnValue['message'] = f'InstructionHandler for {hash} not well formed'
    returnValue['return'] = False
    
  if getHashofInput(body) != hash:
    returnValue['message'] = f'Incorrect hash for InstructionHandler at {hash}'
    returnValue['return'] = False
 
  # TODO confirm signature
  
  
  return returnValue  