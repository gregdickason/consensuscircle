#!/usr/bin/python

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request




# Instantiate the Agent
app = Flask(__name__)

# Generate a globally unique address for this agent 
# In production code this is the agent public key which is assigned by the owning satchell
agent_identifier = str(uuid4()).replace('-', '')
# agent_public_key = 


# Public Methods
@app.route('/converge', methods=['GET'])
def converge():
    # This is where we start the convergence protocol
    print("converging now")
    response = {
                'message': 'Converging on the on the next block',
               }
    
    return jsonify(response), 200
    
@app.route('/instruction', methods=['POST'])
def instruction():
    # Add an instruction to the pool of unprocessed instructions
    print("added an instruction")
    response = {
                'message': 'received instruction',
               }
    
    return jsonify(response), 200
    

@app.route('/agents/register', methods=['POST'])
def register_agents():
    # This is where we start the convergence protocol
    print("registering agents with each other (will be in blockchain")
    response = {
                'message': 'registered agent',
               }
    
    return jsonify(response), 200
    


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
    
