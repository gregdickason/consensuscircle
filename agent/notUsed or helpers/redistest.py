import redis

ENCODING = 'utf-8'

red = redis.StrictRedis(host='localhost', port=6379, db=0, charset=ENCODING, decode_responses=True)

red.sadd("entities", "cam")
red.sadd("entities", "greg")

entities = red.smembers("entities")

print(entities)

for e in entities:
    print(f'e is {e}')


red.hset("cam", "name", "cam")
red.hset("cam", "age", " 22")

print(red.hgetall("cam").type)
