#!/usr/bin/python

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.current_instructions = []
        self.chain = []
        self.agents = set()

        # Load the latest block
        # self.new_block(previous_hash='1', proof=100)

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
        """
        self.current_instructions.append({
            'sender': sender,
            'recipient': recipient,
            'hash': hash,
        })
        
        return len(self.current_instructions)



# Instantiate the Agent
app = Flask(__name__)

# Generate a globally unique address for this agent 
# In production code this is the agent public key which is assigned by the owning satchell (participant)
agent_identifier = str(uuid4()).replace('-', '')
# agent_public_key = 

# Instantiate the Blockchain
blockchain = Blockchain()


# Public Methods
@app.route('/converge', methods=['GET'])
def convergeCircle():
    # This is where we start the convergence protocol (only done to test)
    print("converging now")
    response = {
                'message': 'Converging on the on the next block',
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
        'total_nodes': list(blockchain.agents),
    }
    return jsonify(response), 201
    


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
    
