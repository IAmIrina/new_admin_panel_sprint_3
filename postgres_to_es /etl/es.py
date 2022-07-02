import redis
import pickle


r = redis.Redis(password='f73rt6r3etfr3rtw5r35t', db=1)
# r.flushdb()
# r.mset({'test': {'kolobok': 'a boy'}})
# obj = {'test': {'passed': 100}}
# pickled_object = pickle.dumps(obj['test'])
# r.set('some_key2', pickled_object)
# unpacked_object = pickle.loads(r.get('some_key'))
# print(unpacked_object)

data = {}
for key in r.keys('*'):
    # print(key)
    value = pickle.loads(r.get(key))
    #print(key, value)
    data[key.decode('utf-8')] = value
print(data)
