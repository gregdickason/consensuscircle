from redis import Redis
from rq import Queue
from testRedisprocessor import testConverge 
import time
    
if __name__ == '__main__':
    # Tell RQ what Redis connection to use
    redis_conn = Redis()
    q = Queue('5000', connection=redis_conn)  # no args implies the default queue

    # Delay execution of count_words_at_url('http://nvie.com')
    job = q.enqueue(testConverge, 1)
    result = job.result
    print(f'immediate result: {result}')  # => None

    # Now, wait a while, until the worker is finished
    time.sleep(4)
    result = job.result
    print(f'\nafter 4 secs: {result}')   # => 889    
    
    
    