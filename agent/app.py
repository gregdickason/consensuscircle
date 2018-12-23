#!/usr/bin/python

# local node eventuallty taken over by the cloud. Runs the local server.

# Class for local HTTP connections for the blockchain.  This only accepts inbound communicationss
# Message class does outbound

from flask import Flask, jsonify, request
from agent import Agent
import logging.config
import json
from redis import Redis, RedisError
import os
import socket
from flask_cors import CORS
from flask_restful import Resource, Api
from globalsettings import instructionInfo
from agentUtilities import getHashofInput, signMessage

# Instantiate the Flask App that drives the agent (local instantiation)
app = Flask(__name__)
api = Api(app)
CORS(app)

# Setup Logging
with open('logConfig.json') as json_data:
    logDict = json.load(json_data)
    logging.config.dictConfig(logDict)

logging.info('Instantiating Agent')

# Instantiate the Agent Class
agent = Agent()

# Testing parameters - can turn network off to test if agent is offline (simulate network outage)
networkOn = True

redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

@app.route("/candidateBlocks")
def cblocks():
    return jsonify(str(list(redis.smembers("candidateBlocks"))))

@app.route("/", methods=['GET'])
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    response = {'name' : os.getenv("NAME", "world"), 'hostname' : socket.gethostname(), 'visits' : visits}

    print(jsonify(response))
    return jsonify(response)

#Testing changing code for end to end syncing
@app.route('/ping',methods=['GET'])
def ping():
  global networkOn
  # Testing parameters - is network on
  if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

  return jsonify('pong'), 200

@app.route('/getNetworkStatus',methods=['GET'])
def networkStatus():
   global networkOn
   # Testing parameters - is network on
   if networkOn:
       response = {'network' : "on" }
   else:
       response = {'network' : "off" }
   return jsonify(response)


#Testing Methods - used to simulate network failures by enabling network to be turned off
@app.route('/setNetworkStatus',methods=['POST'])
def changeNetworkStatus():
  global networkOn
  values = request.get_json()
  required = ['network']

  logging.info(f'values received {values}')

  if not all(k in values for k in required):
    return 'Missing fields', 400

  if values['network'] == 'off':
      networkOn = False
  elif values['network'] == 'on':
      networkOn = True

  logging.info(f'network is now {networkOn}')

  response = { 'networkOn' : f'{networkOn}' }
  return jsonify(response), 200


# Public Methods
@app.route('/getConfig', methods=['GET'])
def getConfig():
    global networkOn
    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    agentConfig = agent.getConfig()

    return jsonify(agentConfig)


@app.route('/updateConfig', methods=['POST'])
def updateConfig():
    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    values = request.get_json()

    required = ['level','agentIdentifier','owner','signedIdentifier', 'agentPrivateKey']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    ownerLevel = values['level']  # TODO should come from the agents owners level
    agentIdentifier = values['agentIdentifier']
    ownerID = values['owner']      # TODO confirm that the owner has signed the public key of the agent - have to lookup the key
    signId = values['signedIdentifier']
    agentPrivateKey = values['agentPrivateKey']
    agentResponse = agent.changeConfig(ownerLevel, agentIdentifier, ownerID, signId, agentPrivateKey)

    return jsonify(agentResponse['message']),201

# Routine to get the current instruction pool (used as a part of convergence)
@app.route('/instructionPool', methods=['GET'])
def instructionPool():
    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    agentResponse = agent.instructionPool()

    if agentResponse['success'] == False:
        return jsonify(agentResponse['message']), 400
    else:
        return jsonify(agentResponse['message']), 200

@app.route('/getPendingInstructions', methods=['GET'])
def getPendingInstructions():
    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    agentResponse = agent.instructionPool()

    return jsonify(agentResponse['message']['hashes'])

@app.route('/getEntities', methods=['GET'])
def entityList():
    global networkOn
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    return  jsonify(agent.getEntityList())



@app.route('/entity', methods=['POST'])
def returnEntity():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    values = request.get_json()

    required = ['entity']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    entity = values['entity']

    logging.info(f'returning entity {entity}')

    agentResponse = agent.getEntity(entity)

    # need to do a get on the entities we are tracking that we already know about
    if agentResponse['success'] == False:
        return jsonify(agentResponse['message']), 400
    else:
        return jsonify(agentResponse['message']), 200

@app.route('/getAttributes', methods=['GET'])
def attributeList():
    global networkOn
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    return  jsonify(agent.getAttributes())


@app.route('/attribute', methods=['POST'])
def returnAttribute():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    values = request.get_json()

    required = ['entity', 'attribute']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    entity = values['entity']
    attribute = values['attribute']

    logging.info(f'returning attribute {attribute} for entity {entity}')

    agentResponse = agent.getAttribute(entity, attribute)

    # need to do a get on the entities we are tracking that we already know about
    if agentResponse['success'] == False:
        return jsonify(agentResponse['message']), 400
    else:
        return jsonify(agentResponse['message']), 200


@app.route('/ownerPublicKey',methods=['GET'])
def retrieveOwnerPublicKey():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    logging.info("returning owners public key")
    response = {
            'ownerPublicKey': agent.getOwner()
            }

    return jsonify(response), 200

@app.route('/ownerLevel',methods=['GET'])
def retrieveOwnerLevel():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    logging.info("returning owners level")  # Should we have a better call - ownerDetails with level, owner public key combined?
    response = {
            'ownerLevel': agent.getLevel()
    }
    return jsonify(response), 200


@app.route('/setPrivateKey', methods=['POST'])
def setPrivateKey():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    # set the public and private keys of this node.  Requires signed authority from the owner (and normally only done on setup)
    # first check this is signed by our owner.  If not reject the request
    logging.info("setting the public Key and private key")
    values = request.get_json()

    #TODO the checks of the signature from the owner or we cant let this go through
    # TODO - store in blockstate (this is an update)
    # Check that the required fields are in the POST'ed data
    required = ['privateKey']
    if not all(k in values for k in required):
        return 'Missing key field', 400

    agent.setPrivateKey(values['privateKey'])  # TODO - update the JSON with the details for future use?

    response = {
        'message': f'Agent privateKey set to {agent.getPrivateKey()}'
    }
    return jsonify(response), 201


@app.route('/genesisBlock', methods=['GET'])
def genesisBlock():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    logging.info("genesisBlock retrieved")
    # returns the genesisBlock (which is hardcoded).  This should be used to determine if the calling agent is on the same network as this agent (different networks have different genesisblocks if they are not hard forks of each other)
    response = {
            'blockHash': agent.getGenesisHash()
        }
    return jsonify(response), 200

@app.route('/publishBlock',methods=['POST'])
def processBlock():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    # TODO - need to receive the blockPublished (not stored on file) and process here

    values = request.get_json()

    required = ['blockID']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    blockID = values['blockID']

    logging.info("new block published, retrieve validate and process it")
    # TODO - make parseBlock take the argument of the hash on top of the chain.  If same return immediately to reduce time spent in parseBlock
    agentResponse = agent.processBlock(blockID)

    if agentResponse['success'] == False:
        return jsonify(agentResponse['message']), 400
    else:
        return jsonify(agentResponse['message']), 200


@app.route('/block',methods=['GET'])
def retrieveBlock():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    logging.info("return the Hash of the block at the top of our chain and the block height")
    # TODO generic function for returning all the blocks and contents


    response = agent.getLastBlock()
    return jsonify(response), 200

@app.route('/getPrivateKey',methods=['GET'])
def retrievePrivateKey():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    logging.info("returning privateKey")
    response = {
            'privateKey': agent.getPrivateKey()
    }
    return jsonify(response), 200

#need to add API calls for:
#getting a list of the instruction names
@app.route('/getInstructionNames', methods = ['GET'])
def getInstructionNames():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    instructionSet = instructionInfo()

    return jsonify(instructionSet.getInstructionNames())


#getting a list of the luaHash's matching to the instruction names
@app.route('/getLuaHash', methods = ['POST'])
def getLuaHash():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    values = request.get_json()

    required = ['name']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    logging.info("retrieving a lua hash")

    instructionSet = instructionInfo()
    luaHash = instructionSet.getInstructionHash(values['name'])

    if luaHash == None:
        return jsonify('ERROR: No hash found for that instruction name', 400)
    else:
        return jsonify(luaHash)

#getting the arguments for a particular instruction name
@app.route('/getInstructionArguments', methods = ['POST'])
def getInstructionArguments():
    global networkOn

    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    values = request.get_json()

    required = ['name']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    logging.info("retrieving instruction arguments")

    instructionSet = instructionInfo()
    argumentList = instructionSet.getInstructionArgs(values['name'])

    if argumentList == None:
        return jsonify('ERROR: No instruction with this name', 400)
    else:
        return jsonify(argumentList)

#getting the keys for a particular instruction name
@app.route('/getInstructionKeys', methods = ['POST'])
def getInstructionKeys():
    global networkOn

    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    values = request.get_json()

    required = ['name']
    if not all(k in values for k in required):
        return 'Missing fields', 400

    logging.info("retrieving instruction keys")

    instructionSet = instructionInfo()
    keyList = instructionSet.getInstructionKeys(values['name'])

    if keyList == None:
        return jsonify('ERROR: No instruction with this name', 400)
    else:
        return jsonify(keyList)

@app.route('/executeInstruction', methods=['POST'])
def executeTest():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    input = request.get_json()

    required = ['instruction']
    if not all(k in input for k in required):
        return 'Missing fields', 400

    hash = input['instruction']

    output = agent.executeInstruction(hash)

    return jsonify(output)

@app.route('/addInstruction', methods=['POST'])
def addInstruction():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    #TO DO add a call to agent that can get the unique identifier.
    #eventually need to add some kind of instructionID to ensure uniqueness

    instructionToSend = request.get_json()

    required = ['instruction', 'instructionHash', 'signature']
    if not all(k in instructionToSend for k in required):
        return 'Missing fields', 400

    requiredInstructionParams = ['name', 'keys', 'args', 'sender']
    if not all (j in instructionToSend['instruction'] for j in requiredInstructionParams):
        return 'Missing fields', 400

    instructionSet = instructionInfo()
    requiredKeys = instructionSet.getInstructionKeys(instructionToSend['instruction']['name'])
    requiredArgs = instructionSet.getInstructionArgs(instructionToSend['instruction']['name'])

    if len(requiredKeys) != len(instructionToSend['instruction']['keys']) or len(instructionToSend['instruction']['args']) != len(requiredArgs):
        return jsonify("ERROR: instruction structure is incorrect")

    logging.info(f"instruction to send is {instructionToSend}")

    output = agent.processInstruction(instructionToSend)
    output['hash'] = instructionToSend['instructionHash']

    logging.info(f"attempting to return {output}")

    return jsonify(output)


# TODO remove this routine.  It is being used as to accept agents we want to follow for instruction updates
# build routine into instruction parsing (when we will choose to randomly follow agents?)
@app.route('/agents/register', methods=['POST'])
def register_agents():
    global networkOn

    # Testing parameters - is network on
    if not networkOn:
        response = {'network' : f'{networkOn}'}
        return jsonify(response), 400

    # Register other agents with this agent - add them to the set it maintains
    logging.info('register agent')
    values = request.get_json()

    agents = values.get('agents')

    agentResponse = agent.registerAgents(agents)

    if agentResponse.success == False:
        return jsonify(agentResponse.message), 400
    else:
        return jsonify(agentResponse.message), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # The app is running on open port.  Dont include the 0.0.0.0 if concerned about external access
    app.run(host='0.0.0.0', port=port)
