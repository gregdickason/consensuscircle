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


class Blockchain:
    def __init__(self):
        self.current_instructions = [] # this should be treated as a set and so only added to if the instruction hash is unique (TODO)
        self.instruction_hashes = set() # changed to set as duplicates treated as repeats.  We only add the hash (dont care about the rest)
        self.chain = collections.deque(maxlen = 20)  # only running to a chain depth of 20 in memory 
        self.agents = set()
        self.trusted_agents = set()
        self.untrusted_agents = set()
        self.randomNumbers = []
        self.seed = 0
        self.next_circle = collections.deque(maxlen = 5)
        
        # TODO and HERE to build out what to do with these (from whitepaper?)

    def register_agent(self, address):
        """
        Add a new agent to the list of agents we are working with for consensus.  For now we dont check if they are valid
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.agents.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.agents.add(parsed_url.path)
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

# setup my randomNumbers for my vote for the next chain. 

blockchain.randomNumbers = getRandomNumbers(2)
blockchain.seed = getSeed(2)

# Public Methods
@app.route('/converge', methods=['GET'])
def convergeCircle():
    # This is where we start the convergence protocol (only done to test)
    print("converging now")
    # get hash of instructions from all my followees (registered with me)
    # add these to our list of instructions.  For now we dont check if there are false ones
    
    for url in blockchain.agents:
        request = urllib.request.Request("http://" + url + "/instructions")
        response = urllib.request.urlopen(request)
        body = json.loads(response.read().decode('utf-8'))
        print(f'the returned instructions are {body["instructions"]}')
        i = 0
        while i < len(body["instructions"]):
            blockchain.add_instruction_hash(body["instructions"][i])
            i += 1
        
    
    
    # TODO the below will fail if the number of instructions is 0 as body then undefined
    response = {
                'instructions': f'{body["instructions"]}',
                'nextCircle':f'{blockchain.randomNumbers}'
               }
    
    return jsonify(response), 200


@app.route('/vote', methods=['GET'])
def returnVote():
    print("returning votes")
    # return the blockchain votes (need in future to encode and only return when have all the encoded votes from others or some timout
    response = {
                 'votes':f'{blockchain.randomNumbers}',
                 'seed':f'{blockchain.seed}'
               }
    return jsonify(response),200
    
    
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
        'total_agents': list(blockchain.agents),
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
    
