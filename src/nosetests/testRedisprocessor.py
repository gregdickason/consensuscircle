import requests
from redis import Redis
from rq import Queue

def testConverge(num):
    print(f'Have got {num}')
    if num > 10:
      return num
    else:
      redis_conn = Redis()
      q = Queue('5000', connection=redis_conn)
      q.enqueue(testConverge, num + 1)
      return
    
    
    