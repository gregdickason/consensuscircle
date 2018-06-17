import json

#utility functions for processing instructions - pool is run by the agent
from agentUtilities import getHashofInput

          
# validate Instruction: confirm hash values and signature.  Does not add to pool or update any temp status (done in processInstruction)
def validateInstruction(instruction):
  body = instruction['instruction']
  hash = instruction['instructionHash']
  sign = instruction['sign']
  returnValue = {
        'message': f'Instruction Accepted',
        'return': True
    }
  
  required = ['instructionHash', 'sign', 'instruction']
  if not all(k in instruction for k in required):
    returnValue['message'] = f'Instruction for {hash} not well formed'
    returnValue['return'] = False
    return returnValue
    
  if getHashofInput(body) != hash:
    returnValue['message'] = f'Incorrect hash for Instruction at {hash}'
    returnValue['return'] = False
  
  # TODO confirm signature
  
  
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