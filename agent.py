#!/usr/bin/python

import hashlib
import json
from time import time
from urllib.parse import urlparse
import urllib.request
from uuid import uuid4

from agentUtilities import converge, hashvector, getRandomNumbers, getSeed  # need to setup as cc utilities
import collections
import requests
from flask import Flask, jsonify, request


class trackedAgent:
    def __init__(self):
        self.randomVector = []
        self.randomVectorHashes = []
        self.seed = 0
        self.identifier = str(uuid4()).replace('-', '')  # would be the public key in the real network
        self.instructions = []
        self.instructionHashes = set()
        
    def setRandomVector(self, vector):     
        self.randomVector = vector
        
    def getRandomVector(self):
        return self.randomVector

    def setRandomVectorHashes(self, vectorHashes):     
        self.randomVectorHashes = vectorHashes
        
    def getRandomVectorHashes(self):
        return self.randomVectorHashes
      
    def setIdentifier(self, id):     
        self.identifier = id
        
    def getIdentifier(self):
        return self.identifier
      
    def setSeed(self, s):     
        self.seed = s
            
    def getSeed(self):
        return self.seed
        
    def setInstructions(self, ins):     
        self.instructions = ins
        
    def getInstructions(self):
        return self.instructions
    
    def setInstructionHashes(self, ih):     
        self.instructionHashes = ih
            
    def getInstructionHashes(self):
        return self.instructionHashes
    
    

class Blockchain:
    def __init__(self):
        self.current_instructions = [] # this is treated as a set and so only added to if the instruction hash is unique
        self.instruction_hashes = set() # changed to set as duplicates treated as repeats.  We only add the hash (dont care about the rest)
        self.chain = collections.deque(maxlen = 20)  # only running to a chain depth of 20 in memory 
        self.followedAgents = set()   # vector of tracked agents we listen to
        self.trusted_agents = set()
        self.untrusted_agents = set()
        # using a trackedCircle list (will have objects for each agent: the UID of the agent, the random numbers from the agent, the hashes of the random number, the seed, 8th is the list of instructions, 9th is the hash of the list
        self.trackedCircleAgents = []  # list that manages the outputs from other agents to allow gossip checks and for the convergence protocol to determine the next circle         
        self.randomMatrix = []
        self.randomMatrixHash = []        
        self.seed = 0
        
        
        # TODO and HERE to build out what to do with these (from whitepaper?)

    def register_agent(self, address):
        """
        Add a new agent to the list of agents we are working with for consensus.  For now we dont check if they are valid
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
        Adds instructions hashes we are not going to track in this node (only the hash is in the blockchain directly for now
        param hash: sha256 hash of the instruction
        """
        self.instruction_hashes.add(hash)
        return len(self.instruction_hashes)
         



# Instantiate the Agent
app = Flask(__name__)

# Generate a globally unique address for this agent 
# In production code this is the agent public key which is assigned by the owning satchell (participant)
agent_identifier = str(uuid4()).replace('-', '')
print(f'my unique agent ID is {agent_identifier}')


# Instantiate the Blockchain
blockchain = Blockchain()

# Instantiate the tracked agents in my circle - need to read some of the parameters in the final code
maxAgentsInCircle = 5
for x in range(0,maxAgentsInCircle):
    blockchain.trackedCircleAgents.append(trackedAgent())

# setup my randomNumbers, my hashed random numbers, and seed for my vote for the next chain. 
blockchain.randomMatrix = [g for g in getRandomNumbers(2,5)]
blockchain.seed = getSeed(2)
blockchain.randomMatrixHash = [g for g in hashvector(blockchain.randomMatrix, blockchain.seed)]
print(f'Blockchain random hash is {blockchain.randomMatrixHash}')

# Public Methods
@app.route('/converge', methods=['GET'])
def convergeCircle():
    # This is where we start the convergence protocol (only done to test)
    print("converging now")
    
    # get hash of instructions from all my followees (registered with me)
    # add these to our list of instructions.  For now we dont check if there are false ones  (not for simulation but for final code this would be in)
    
    for url in blockchain.followedAgents:
        request = urllib.request.Request("http://" + url + "/instructions")
        response = urllib.request.urlopen(request)
        body = json.loads(response.read().decode('utf-8'))
        print(f'the returned instructions are {body["instructions"]}')
        i = 0
        while i < len(body["instructions"]):
            blockchain.add_instruction_hash(body["instructions"][i])
            i += 1
        
    # converge on next circle - get random numbers from our followees to make up matrix.  Need to get theirs and from their followees
    # TODO HERE 
    
    # TODO the below will fail if the number of instructions is 0 as body then undefined
    response = {
                'instructions': f'{body["instructions"]}',
                'nextCircle':f'{blockchain.randomMatrix}'
               }
    
    return jsonify(response), 200


@app.route('/vote', methods=['GET'])
def returnVote():
    # only return if we have already received all the hashes from the circle
    print("Returning votes")
    # return the blockchain votes (need in future to encode and only return when have all the encoded votes from others or some timout
    response = {
                 'votes':list(blockchain.randomMatrix),
                 'seed':blockchain.seed
               }
    return jsonify(response),200

@app.route('/hashedVote', methods=['GET'])
def returnHashedVote():
    print(f'Blockchain random hash is {blockchain.randomMatrixHash}')
    # return the hashed vote
    response = {
                  'voteHashes': list(blockchain.randomMatrixHash)
               }   
    
    return jsonify(response), 200

    
@app.route('/entity', methods=['GET'])
def returnEntities():
    print("returning entities")
    # need to do a get on the entities we are tracking
    response = {
                'entity': 'abc',
               }
    
    return jsonify(response), 200

@app.route('/instructions',methods=['GET'])
def retrieveInstructions():
    print("returning instructions")
    response = {
            'instructions': list(blockchain.instruction_hashes)
    }
    return jsonify(response), 200
    
    
@app.route('/instruction', methods=['POST'])
def instruction():
    # Add an instruction to the pool of unprocessed instructions
    print("added an instruction")
    values = request.get_json()
    
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'hash']
    if not all(k in values for k in required):
        return 'Missing mandatory fields in the instruction', 400
    
    # Create a new Instruction
    numberInstructions = blockchain.add_instruction(values['sender'], values['recipient'], values['hash'])
    
    response = {
        'message': f'Agent currently has {numberInstructions} instructions in the unprocessed pool',
        'instructions': list(blockchain.current_instructions)
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

    for agent in agents:
        blockchain.register_agent(agent)

    response = {
        'message': 'New agents have been added',
        'total_agents': list(blockchain.followedAgents),
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
    
