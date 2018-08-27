from rejson import Client, Path
import json

rj = Client(host='localhost', port=6379, decode_responses=True)

# Set the key `obj` to some object
obj = {
    'answer': 42,
    'arr': [None, True, 3.14],
    'truth': {
        'coord': 'out there'
    }
}

jsondata = json.dumps(obj)

rj.jsonset('obj', Path('A2AA'), obj)

# Get something
temp = rj.jsonget('obj', Path('A2AA.truth.coord'))

print (f'Is there anybody... {temp}?')

# Delete something (or perhaps nothing), append something and pop it
rj.jsondel('obj', Path('.arr[0]'))
rj.jsonarrappend('obj', Path('.arr'), 'something')
popped = rj.jsonarrpop('obj', Path('.arr'))
print(f'{popped} popped!')

# Update something else
rj.jsonset('obj', Path('.answer'), 2.17)

# And use just like the regular redis-py client
jp = rj.pipeline()
jp.set('foo', 'bar')
jp.jsonset('baz', Path.rootPath(), 'qaz')
jp.execute()

