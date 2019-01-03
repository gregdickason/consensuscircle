# RedisLoadScript is a helper function to prepopulate redis with LUA scripts that are the data update parts of instructions
import redis
import json
import logging.config

ENCODING = 'utf-8'

# setup logging
with open('logConfig.json') as json_data:
  logDict = json.load(json_data)
  logging.config.dictConfig(logDict)

def importScripts(filename):
    red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)
    # the filename for the scripts holds all the script names.  We iterate through all of these and create scripts in
    # redis for each one.  We output the script SHA and corresponding instruction name in json structure that can be referenced by the client.
    logging.debug(f'loaded file {filename}, iterating through and loading scripts')

    alist = []
    shalist = {}

    with open(filename) as f:
      alist = [line.rstrip() for line in f]

    logging.debug(f'loaded scripts {alist}')

    for scriptfile in alist:
        logging.debug(f'opening {scriptfile}')
        with open('lua/' + scriptfile + '.lua', 'r') as scriptf:
            script = scriptf.read()
            # logging.debug(f'script is {script}')
            scriptHash = red.script_load(script)
            logging.debug(f'Loaded {scriptfile} script - hash is {scriptHash}')
            shalist[scriptfile] = scriptHash
            red.sadd("instructions", scriptfile)
            red.hset("instruction:" + scriptfile, "luaHash", scriptHash)

        # running the json loads/dumps ensures that the args and keys
        # files are appropriately formatted
        with open('lua/' + scriptfile + '_args.json', 'r') as argsf:
            # logging.debug(f'{argsf.read()}')
            args = json.loads(argsf.read())
            red.hset("instruction:" + scriptfile, "args", json.dumps(args))

        with open('lua/' + scriptfile + '_keys.json', 'r') as keysf:
            keys = json.loads(keysf.read())
            red.hset("instruction:" + scriptfile, "keys", json.dumps(keys))

    return

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', default='lua/scripts.txt', help='filename of script to load')
    args = parser.parse_args()
    file = args.file

    # The app is running on open port.  Dont include the 0.0.0.0 if concerned about external access
    importScripts(file)
