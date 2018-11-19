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
  # Testing parameters - is network on
  if not networkOn:
    response = {'network' : f'{networkOn}'}
    return jsonify(response), 400

  return jsonify('pong'), 200

#Testing Methods - used to simulate network failures by enabling network to be turned off
@app.route('/networkOn',methods=['POST'])
def networkOn():
  values = request.get_json()
  required = ['network']

  logging.info(f'values received {values}')

  if not all(k in values for k in required):
    return 'Missing fields', 400

  if values['network'] == 'off':
    networkOn = False
  elif values['network'] == 'on':
    networkOn = True

  response = { 'networkOn' : f'{networkOn}' }
  return jsonify(response), 200


# Public Methods
@app.route('/getConfig', methods=['GET'])
def getConfig():
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
   ownerPKey = values['owner']      # TODO confirm that the owner has signed the public key of the agent - have to lookup the key
   signId = values['signedIdentifier']
   agentPrivKey = values['agentPrivateKey']
   agentResponse = agent.changeConfig(ownerLevel, agentIdentifier, ownerPKey, signId, agentPrivKey)

   return jsonify(agentResponse['message']), 201

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


@app.route('/entity', methods=['GET'])
def returnEntity():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    entity = request.args.get('entity')

    logging.info(f'returning entity {entity}')

    agentResponse = agent.getEntity(entity)

    # need to do a get on the entities we are tracking that we already know about
    if agentResponse['success'] == False:
        return jsonify(agentResponse['message']), 400
    else:
        return jsonify(agentResponse['message']), 200



@app.route('/ownerPublicKey',methods=['GET'])
def retrieveOwnerPublicKey():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    logging.info("returning owners public key")
    response = {
            'ownerPublicKey': agent.owner
    }
    return jsonify(response), 200


@app.route('/ownerLevel',methods=['GET'])
def retrieveOwnerLevel():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    logging.info("returning owners level")  # Should we have a better call - ownerDetails with level, owner public key combined?
    response = {
            'ownerLevel': agent.level
    }
    return jsonify(response), 200


@app.route('/setPKey', methods=['POST'])
def setPKey():
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
    required = ['pkey']
    if not all(k in values for k in required):
        return 'Missing pkey field', 400

    agent.agent_identifier = values['pkey']  # TODO - update the JSON with the details for future use?

    response = {
        'message': f'Agent pkey set to {agent.agent_identifier}'
    }
    return jsonify(response), 201


@app.route('/genesisBlock', methods=['GET'])
def genesisBlock():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    logging.info("genesisBlock retrieved")
    # returns the genesisBlock (which is hardcoded).  This should be used to determine if the calling agent is on the same network as this agent (different networks have different genesisblocks if they are not hard forks of each other)
    response = {
            'blockHash': agent.genesisBlock.blockHash
        }
    return jsonify(response), 200

@app.route('/blockPublished',methods=['GET'])
def processBlock():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    # TODO - need to receive the blockPublished (not stored on file) and process here

    blockID = request.args['blockID']

    logging.info("new block published, retrieve validate and process it")
    # TODO - make parseBlock take the argument of the hash on top of the chain.  If same return immediately to reduce time spent in parseBlock
    agentResponse = agent.processBlock(blockID)

    if agentResponse['success'] == False:
      return jsonify(agentResponse['message']), 400
    else:
      return jsonify(agentResponse['message']), 200


@app.route('/block',methods=['GET'])
def retrieveBlock():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    logging.info("return the Hash of the block at the top of our chain and the block height")
    # TODO generic function for returning all the blocks and contents


    response = {
            'lastBlock': agent.chain[0].blockHash,
            'blockHeight': agent.chain[0].blockHeight,
            'circleDistance': agent.chain[0].circleDistance
    }
    return jsonify(response), 200


@app.route('/PKey',methods=['GET'])
def retrievePKey():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    logging.info("returning pkey")
    response = {
            'pkey': agent.agent_identifier
    }
    return jsonify(response), 200


@app.route('/instruction', methods=['POST'])
def instruction():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    # Add an instruction to the pool of unprocessed instructions
    logging.info("received an instruction to add")
    values = request.get_json()

    agentResponse = agent.processInstruction(values)

    if not agentResponse['success']:
      return jsonify(agentResponse['message']), 400
    else:
      return jsonify(agentResponse['message']), 200

@app.route('/instructionHandler', methods=['POST'])
def instructionHandler():
    # Testing parameters - is network on
    if not networkOn:
      response = {'network' : f'{networkOn}'}
      return jsonify(response), 400

    # Add an instruction to the pool of unprocessed instructions
    logging.info("received an instructionHandler to add")
    values = request.get_json()

    agentResponse = agent.processInstructionHandler(values)

    if not agentResponse['success']:
      return jsonify(agentResponse['message']), 400
    else:
      return jsonify(agentResponse['message']), 200


# TODO remove this routine.  It is being used as to accept agents we want to follow for instrution updates
# build routine into instruction parsing (when we will choose to randomly follow agents?)
@app.route('/agents/register', methods=['POST'])
def register_agents():
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
