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
from trackedAgent import trackedAgent

#utility functions
from agentUtilities import converge, hashvector, getRandomNumbers, getRandomNumber, getSeed, returnHashDistance  # need to setup as cc utilities


class Agent:
    def __init__(self):
        self.current_instructions = [] # Pool of unprocessed instructions we are aware of
        self.instruction_hashes = set() # Set as duplicates treated as repeats and not added to the current_instructions pool. 
        self.chain = collections.deque(maxlen = 20)  
        
        self.followedAgents = set()   #  set of agents we follow for updates when operating in the circle.  
        
        self.trackedCircleAgents = {}  # dictionary(map) that this agent uses to converge: checking the outputs from other agents to allow gossip checks and for the convergence protocol to determine the next circle         
        
        # On convergence we populate these:
        self.randomMatrix = []
        self.randomMatrixHash = []        
        self.seed = 0
        
        self.owner = ''  # This is part of setup file for each agent and holds the public key of the owner.  Needs to sign public key of the agent to ensure that this agent is operating on their behalf (offered as proof)
        self.agent_identifier = ''  # set by the owner through a call (so by the test scripts for now)
        self.level = 0  # this is the level of the agent.  Starts at 5 which is ineligible for circle membership
        self.inCircle = False  # we are not in a circle by default
        
        # Register an agent to follow.  This is our direct connections to other agents in the circle
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
       
    def add_instruction (self, sender, recipient, hash):
        """
        Creates an instruction to add to the unprocessed instructions pool.  For simulation does not propagate to other agents
        
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
            'recipient': recipient,
            'hash': hash,
        })
        
        self.instruction_hashes.add(hash)
        print(f'instruction hashes are {self.instruction_hashes}')
        return len(self.current_instructions)
    
    
    def add_instruction_hash(self, hash):
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
agent.agent_identifier = app.config.get('pkey')

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
        body = json.loads(response.read().decode('utf-8'))
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
            body = json.loads(response.read().decode('utf-8'))
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
        body = json.loads(response.read().decode('utf-8'))   # check this doesnt override to the last call
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
    


@app.route('/setPKey', methods=['POST'])
def setPKey():
    # set the public key of this node.  Requires signed authority from the owner (and normally only done on setup)
    print("setting the public Key")
    values = request.get_json()
    
    # Check that the required fields are in the POST'ed data
    required = ['pkey']
    if not all(k in values for k in required):
        return 'Missing pkey field', 400
    
    agent.agent_identifier = values['pkey']
    
    response = {
        'message': f'Agent pkey set to {agent.agent_identifier}'
    }
    return jsonify(response), 201


@app.route('/blockPublished',methods=['GET'])
def processBlock():
    print("new block published, retrieve validate and process it")
    
    # TODO Block Validation in lastBlock() method and then validate that this block is valid (hashpointer, block agent distance, etc).  Also if should fork to this block
    agent.chain.append(lastBlock())
    
    # CHECK if we should be in the block -- start with how far are we from the actual block ID 
    
    #agent.inCircle = checkBlockMembership(agent.chain[0].outputMatrix[agent.level], agent.agent_identifier)
    distance = returnHashDistance(agent.chain[0].outputMatrix[agent.level][0], agent.agent_identifier)  # only for now taking the first in the level - need to parse this per slot in a level for distances if there are more than 1 (based on blockchain parameters)
    
    # now check if there are any closer agents (Will be a database / noSQL call in the production code)

    response = {
            'lastBlock': agent.chain[0].blockHash,
            'levelDistance': distance
    }
    return jsonify(response), 200


@app.route('/block',methods=['GET'])
def retrieveBlock():
    print("return the Hash of the block at the top of our chain and the block height")
    # TODO generic function for returning all the blocks and contents
    

    response = {
            'lastBlock': agent.chain[0].blockHash,
            'blockHeight': agent.chain[0].blockHeight
    }
    return jsonify(response), 200


@app.route('/PKey',methods=['GET'])
def retrievePKey():
    print("returning pkey")
    response = {
            'pkey': agent.agent_identifier
    }
    return jsonify(response), 200

    
@app.route('/instruction', methods=['POST'])
def instruction():
    # Add an instruction to the pool of unprocessed instructions
    print("received an instruction to add")
    values = request.get_json()
    
    
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'hash']
    if not all(k in values for k in required):
        return 'Missing mandatory fields in the instruction', 400
    
    # Create a new Instruction
    numberInstructions = agent.add_instruction(values['sender'], values['recipient'], values['hash'])
    
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
    
