# test python code to execute a LUA script - takes a Keys and an ARGS argument
# From https://redislabs.com/ebook/part-3-next-steps/chapter-11-scripting-redis-with-lua/11-1-adding-functionality-without-writing-c/11-1-1-loading-lua-scripts-into-redis/
import json
import redis
ENCODING = 'utf-8'

def scriptCall(scriptHash, keys=[], args=[]):
  red = redis.StrictRedis(host='redis', port=6379, db=0, charset=ENCODING, decode_responses=True)
  #When calling the loaded script, we must provide a connection, a set of keys that the script will manipulate, and any other arguments to the function.
  output = red.execute_command("EVALSHA", scriptHash, len(keys), *(keys+args))
  print(f'script output is {output}')

  return


if __name__ == '__main__':

    # fw hardcoded examples of calling LUA
    scriptCall('59f3eb590a68c71483463553f9b2d715550be5ae', [], [])  # outputs HEllo - from 'test.lua'
    scriptCall('fdba8af41d881621cdc42bf03135a9c325f4a87a', [], [])  # initialises the data base
    # Transfer 1500 from Cameron to Greg
    scriptCall('8292d2c55210392e3bb7c7e9c98c4d5cf4154431', ['e7b1eb096bcb82eead157ec870789b3d8d1ce0d914848c2cc10ec751e5401507','d66a1f7f777eba5cc5349000412342b460b12e6270adb338a9ad506cf652169f'],['wallets.default.balance','wallets.default.balance','1500']) # transfer funds from entity Keys[1], wallet Args[1], to entity Keys[2], wallet Args[2], amount Args[3]
