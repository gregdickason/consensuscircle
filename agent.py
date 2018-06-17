#!/usr/bin/python

import hashlib
import json
from time import time
from urllib.parse import urlparse
import urllib.request
from uuid import uuid4

import collections
import requests
from flask import Flask, jsonify, request


# classes managing the aspects of the blockchain an agent needs in this simulation: the lastBlock, the agents they are following for updates.
from lastBlock import lastBlock
from parseBlock import parseBlock
from genesisBlock import genesisBlock
from blockState import blockState
from trackedAgent import trackedAgent


#utility functions
from agentUtilities import converge, hashvector, getRandomNumbers, getRandomNumber, getSeed, returnHashDistance, returnCircleDistance 
from processInstruction import validateInstruction

class Agent:
    def __init__(self):
        self.current_instructions = [] # Pool of unprocessed instructions we are aware of, sent from other agents (do through non http protocol?)
        self.instruction_hashes = set() # Set as duplicates treated as repeats and not added to the current_instructions pool. 
        self.chain = collections.deque(maxlen = 100) # this should be a setting and is for the most recent blocks
        self.entityInstructions = 100 # global ccEntity setting needs to be read
        
        self.followedAgents = set()   #  set of agents we follow for updates when operating in the circle.  
        
        self.trackedCircleAgents = {}  # dictionary(map) that this agent uses to converge: checking the outputs from other agents to allow gossip checks and for the convergence protocol to determine the next circle         
        self.nextCircle = []  # next Circle.  May or may not include us
        
        # On convergence when we are in a circle we populate these:
        self.randomMatrix = []
        self.randomMatrixHash = []        
        self.seed = 0
        
        # this is the level of the agent.  Starts at 5 which is ineligible for circle membership
        self.inCircle = False  # we are not in a circle by default
        with open('agentConfig.json') as json_data:
            self.config = json.load(json_data)  # TODO put in exception handling and error checking if file is malformed
            self.level = self.config['level']   # TODO this should be confirmed by the agent from the owners level (not independent).  In the blockState object
            self.agent_identifier = self.config['agentIdentifier']
            self.owner = self.config['ownerPKey']      # TODO confirm that the owner has signed the public key of the agent
	               
        self.blockState = blockState()
        self.genesisBlock = genesisBlock()
        
        # add to the chain on startup if we have no state we can read from
        if self.blockState.blockHeight == 0:
            self.chain.append(self.genesisBlock)
        # TODO elif we already have state then we need to get other blocks from agents to see if we are up to date
        
        # Register an agent to follow.  This is our direct connections to other agents in the circle.  #TODO should be from the knownAgents.json config and using helper classes as this will be not always HTTP
    def register_agent(self, address):
        """
        Add a new agent to the list of agents we are following for instructions.  For now we dont check if they are valid
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
              
        if parsed_url.netloc:
            self.followedAgents.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.followedAgents.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
       
    def add_instruction (self, sender, hash):
        """
        Creates an instruction to add to the unprocessed instructions pool.  Now just keyed on hash 
        TODO: Process Entity update 
        
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param hash: sha256 hash of the instruction contents (for convergence simulation not adding instruction this is for uniqueness)
        Note that the hash is how the final consensus circle code will manage instructions in sets (so immutable and guaranteed to be unique and idempotently added)
        """
        
        # check if the hash has already been received for this instruction and if so then dont append
        if hash in self.instruction_hashes:
            print(f'Received instruction already have, instruction hashes are {self.instruction_hashes}')
            return len(self.current_instructions)
        
        self.current_instructions.append({
            'sender': sender,
            'hash': hash
        })
        
        self.instruction_hashes.add(hash)
        print(f'instruction hashes are {self.instruction_hashes}')
        return len(self.current_instructions)
    
    
    def add_instruction_hash(hash):
        """
        Adds instructions hashes we are not going to track in this agent (only the hash is in the blockchain directly for now
        param hash: sha256 hash of the instruction
        """
        self.instruction_hashes.add(hash)
        return len(self.instruction_hashes)
         



# Instantiate the Agent
app = Flask(__name__)


# Instantiate the Agent Class
agent = Agent()

# Instantiate the tracked agents in my circle 
maxAgentsInCircle = 4   # set to 1 below number as we are a member of the circle
#for x in range(0,maxAgentsInCircle):
#    agent.trackedCircleAgents.append(trackedAgent())


# setup my randomNumbers, my hashed random numbers, and seed for my vote for the next chain. 
agent.randomMatrix = [g for g in getRandomNumbers(2,5)]
agent.seed = getSeed(2)
agent.randomMatrixHash = [g for g in hashvector(agent.randomMatrix, agent.seed)]
print(f'Agents random hash is {agent.randomMatrixHash}')

# Public Methods
@app.route('/convergeUIDs', methods=['GET'])
def convergeUIDs():
    # This is where we find all the UIDs of the agents in the blockchain.  If we dont have them we return 202, if we do we return 200 (Check appropriate code).
    # If the return is 202 we expect to be called again to determine if we have converged  (in final code we could loop inside an EC2 instance or using some form of loop around a queue)
    print("converging on UIDs")
    # get UID, and ask for other UIDs
    for url in agent.followedAgents:
        request = urllib.request.Request("http://" + url + "/entity")
        response = urllib.request.urlopen(request)
        body = json.loads(response.read().decode('utf-8'))   # Do in utilites and use ENCODING for utf-8
        # Check if we have seen this entity already (in the agent.trackedCircleAgents)
        if body["entity"] in agent.trackedCircleAgents:
            print(f'ALready tracking Agent with UID {body["entity"]}')
        else:
            agent.trackedCircleAgents[body["entity"]] = trackedAgent()
            
        print(f'the returned uid for followed URL is {body["entity"]}')
        print(f'the returned uid for trackedEntities is {body["trackedEntities"]}')
        
        if body["entity"] not in agent.slots:
            agent.slots.add(body["entity"])
        
        i = 0    
        while i < len(body["trackedEntities"]):
            agent.slots.add(body["trackedEntities"][i])
            i += 1
    print(f'Agent slots are {agent.slots}')
    
    response = {
	         'uids': f'[{agent.slots}]'  
	       }
	       
    if len(agent.slots) < maxAgentsInCircle:
        return jsonify(response), 202
    else:
        return jsonify(response), 200


@app.route('/convergeInstructions', methods=['GET'])
def convergeCircleInstructions():
    # This is where we start the convergence protocol (only done to test)
    print("converging now")
    
    # Create Slots and populate with UID, Instructions, Random Numbers, etc
    
    
    # get UID, and ask for other UIDs
    for url in agent.followedAgents:
            request = urllib.request.Request("http://" + url + "/instructions")
            response = urllib.request.urlopen(request)
            body = json.loads(response.read().decode('utf-8'))   # do in utilities and use ENCODING for utf-8
            print(f'the returned instructions are {body["instructions"]}')
            i = 0
            while i < len(body["instructions"]):
                agent.add_instruction_hash(body["instructions"][i])
                i += 1
   
    # TODO the below will fail if the number of instructions is 0 as body then undefined
    if len(body["instructions"]) > 0:
        response = {
                    'instructions': f'{body["instructions"]}'
                    #'nextCircle':f'{agent.randomMatrix}'
                   }
    else:                
        response = {
	            'instructions': '[]'
	            #'nextCircle':f'{agent.randomMatrix}'
                   }
    return jsonify(response), 200


@app.route('/convergeHashedVotes', methods=['GET'])
def convergeHashedVotes():
    # Method to get the hahedVotes for all agents in circle
    for url in agent.followedAgents:
        request = urllib.request.Request("http://" + url + "/hashedVote")
        response = urllib.request.urlopen(request)
        body = json.loads(response.read().decode('utf-8'))   # check this doesnt override to the last call, do in utilities and use ENCODING for utf-8
        print(f'the returned hashes are {body["voteHashes"]}')
        
        # return only the voteHashes from our followed entities - TODO: add to the trackedCircleAgents
        response = {
                    'voteHashes': f'{body["voteHashes"]}',
                   }
        
        return jsonify(response), 200


@app.route('/vote', methods=['GET'])
def returnVote():
    # only return if we have already received all the hashes from the circle
    # only return if we are in the circle
    print("Returning votes")
    # return the agent votes (need in future to encode and only return when have all the encoded votes from others or some timout
    response = {
                 'votes':list(agent.randomMatrix),
                 #'followeesVotes':list(
                 #'seed':agent.seed
               }
    return jsonify(response),200

@app.route('/hashedVote', methods=['GET'])
def returnHashedVote():
    print(f'Agents random hash is {agent.randomMatrixHash}')
    # return the hashed vote
    response = {
                  'voteHashes': list(agent.randomMatrixHash)
               }       
    return jsonify(response), 200

    
@app.route('/entity', methods=['GET'])
def returnEntities():
    print("returning entities")
    # need to do a get on the entities we are tracking that we already know about            
    response = {
                'entity': agent.agent_identifier,
                'trackedEntities':[slot for slot in agent.slots if len(slot) > 0] # GREG HERE - treating as set and not 
               }
    
    return jsonify(response), 200

@app.route('/instructions',methods=['GET'])
def retrieveInstructions():
    print("returning instructions")
    response = {
            'instructions': list(agent.instruction_hashes)   # We just return the instruction hashes.  Individual instructions are returned on gets per instruction
    }
    return jsonify(response), 200
    
@app.route('/ownerPublicKey',methods=['GET'])
def retrieveOwnerPublicKey():
    print("returning owners public key")
    response = {
            'ownerPublicKey': agent.owner   
    }
    return jsonify(response), 200


@app.route('/ownerLevel',methods=['GET'])
def retrieveOwnerLevel():
    print("returning owners public key")  # Should we have a better call - ownerDetails with level, owner public key combined?
    response = {
            'ownerLevel': agent.level 
    }
    return jsonify(response), 200


@app.route('/setPKey', methods=['POST'])
def setPKey():
    # set the public and private keys of this node.  Requires signed authority from the owner (and normally only done on setup)
    # first check this is signed by our owner.  If not reject the request 
    print("setting the public Key and private key")
    values = request.get_json()
    
    #TODO the checks of the signature from the owner
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
    # returns the genesisBlock (which is hardcoded).  This should be used to determine if the calling agent is on the same network as this agent (different networks have different genesisblocks if they are not hard forks of each other)
    response = {
            'blockHash': agent.genesisBlock.blockHash
        }
    return jsonify(response), 200

@app.route('/blockPublished',methods=['GET'])
def processBlock():
    blockID = request.args['blockID']
    
    print("new block published, retrieve validate and process it")
    # TODO - make parseBlock take the argument of the hash on top of the chain.  If same return immediately to reduce time spent in parseBlock
    newBlock = parseBlock(blockID)
    
    # is the block Valid?
    if newBlock.blockPass == False:
        response = {
	            'chainLength' : len(agent.chain) - 1,
	            'lastBlock': agent.chain[len(agent.chain)-1].blockHash,
	            'error': newBlock.blockComment
	}
        return jsonify(response), 422  # unprocessable entity 
    
   
    # if this is the same blockHeight we have already processed - check if circle distance is closer (i.e. there is more random outputs and therefore more 
    # coinbase transactions to recognise, plus we need to reprocess who should be in the circle)
    # TODO - Circle Distance Check, Look at even lower in the stack as lower height still forkable
    if newBlock.blockHeight == agent.chain[len(agent.chain)-1].blockHeight:
        response = {
            'chainLength' : len(agent.chain) - 1,
            'lastBlock': agent.chain[len(agent.chain)-1].blockHash,
            'circleDistance': agent.chain[len(agent.chain)-1].circleDistance
        }
        return jsonify(response), 201
    elif newBlock.previousBlock != agent.chain[len(agent.chain)-1].blockHash:
        # This is not building on the top of our chain.  Need to work out if in the chain and deeper down, a fork or are we missing a block.  Do we need to sync
        # TODO If not then calculate the circleDistance and if lower then use this block (accept the fork)
        # TODO on this (look at blockheight, etc).  Also need to make sure we cant be attacked with something random that consumes processing power
        # if lower down we need to reprocess the coinbase transactions
        response = {
	            'message' : 'Received block not in chain.  need to manage it TODO'
	           }
        return jsonify(response), 202
    
    # Normal processing, new block built on our chain.  READ NOTES
    
    # Newblock circle distance needs to be calculated off the old block outputMatrix
    newBlock.circleDistance = returnCircleDistance(newBlock.ccKeys, agent.chain[len(agent.chain)-1].outputMatrix, newBlock.instructionCount,agent.entityInstructions)
    print(f'\n ** NEW BLOCK PUBLISHED. ** Block distance = {newBlock.circleDistance}\n')
        
    # TODO confirm that the block is shortest distance 
    agent.chain.append(newBlock)
    
    # TODO process instructions and remove from unprocessed pool if in the block  (TODO work out how to roll back if a new block is better)
    
    # CHECK if we should be in the block -- start with how far are we from the actual block ID 
    
    #agent.inCircle = checkBlockMembership(agent.chain[0].outputMatrix[agent.level], agent.agent_identifier)
    #distance = returnHashDistance(agent.chain[0].outputMatrix[agent.level][0], agent.agent_identifier)  
    
    # now check if there are any closer agents (Will be a database / noSQL call in the production code)
    
    # assume there are not and we are in the circle.
    # TODO: Trigger event to check if we are in the next circle and start processing
    # TODO: next circle could have race condition for a promoted agent.  Agents need some N number of blocks old before being eligible (to stop race condition)
    agent.nextCircle = agent.blockState.nextCircle(newBlock.outputMatrix, [])  # No excluded agents for now
    
    print(f'\nNext circle is {agent.nextCircle}\n')

    response = {
            'chainLength' : len(agent.chain) - 1,
            'lastBlock': agent.chain[len(agent.chain)-1].blockHash,
            'circleDistance': newBlock.circleDistance
    }
    return jsonify(response), 200


@app.route('/block',methods=['GET'])
def retrieveBlock():
    print("return the Hash of the block at the top of our chain and the block height")
    # TODO generic function for returning all the blocks and contents
    

    response = {
            'lastBlock': agent.chain[0].blockHash,
            'blockHeight': agent.chain[0].blockHeight,
            'circleDistance': agent.chain[0].circleDistance
    }
    return jsonify(response), 200


@app.route('/PKey',methods=['GET'])
def retrievePKey():
    print("returning pkey")
    response = {
            'pkey': agent.agent_identifier
    }
    return jsonify(response), 200



# TODO: setup instruction handling and instructions.  2 sides to allow data management.  
# For example, and offer from a company will be an instrcution handler: 'if you have these attributes and you send me this proof through an instruction, this handler will do XYZ'
# The above allows people to 'always opt in' through delegating agents to share some of their data (with shared keys), to opt in when they want, to partiipate in anonymous surveys (through anonymous matching of their attributes), to contribute and earn from models,or to never opt in but understand the value of the data they have
@app.route('/instruction', methods=['POST'])
def instruction():
    # Add an instruction to the pool of unprocessed instructions
    print("received an instruction to add")
    values = request.get_json()
    
    # TODO - validateInstruction
    # Check that the required fields are in the POST'ed data
    validInstruction = validateInstruction(values)
    if not validInstruction['return']:
      response = {
	      'message': validInstruction['message'],
        }  
      return  jsonify(response),422
    
    # Create a new Instruction in the Pool (dont process just add the hash)
    # TODO Process the instruction with the update
    numberInstructions = agent.add_instruction(values['instruction']['source'],values['instructionHash'])
    
    response = {
        'message': f'Agent currently has {numberInstructions} instructions in the unprocessed pool',
        'instructions': list(agent.current_instructions)
    }
    return jsonify(response), 201
    
    

@app.route('/agents/register', methods=['POST'])
def register_agents():
    # Register other agents with this agent - add them to the set it maintains 
    print("registering agents with each other (will be in blockchain")
    values = request.get_json()

    agents = values.get('agents')
    if agents is None:
        return "Error: Please supply a valid list of agents", 400

    for ele in agents:
        agent.register_agent(ele)

    response = {
        'message': 'New agents have been added',
        'total_agents': list(agent.followedAgents),
    }
    return jsonify(response), 201
    


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    # The app is running on open port.  Dont include the 0.0.0.0 if concerned about external access
    app.run(host='0.0.0.0', port=port)
    
