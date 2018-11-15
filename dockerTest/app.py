from flask import Flask, jsonify
from redis import Redis, RedisError
import os
import socket
from flask_cors import CORS
import json
from flask_restful import Resource, Api

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)
api = Api(app)
CORS(app)

def returnData(data):
    print("Access-Control-Allow-Origin: *")
    print("Content-Type: application/json")
    print('\n')
    print(json.dumps(data))

@app.route("/", methods=['GET'])
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    # html = "<h3>Hello {name}!</h3>" \
    #        "<b>Hostname:</b> {hostname}<br/>" \
    #        "<b>Visits:</b> {visits}"
    # return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)

    response = {'name' : os.getenv("NAME", "world"), 'hostname' : socket.gethostname(), 'visits' : visits}

    print(jsonify(response))
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
