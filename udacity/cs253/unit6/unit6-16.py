
# QUIZ implement the basic memcache functions

CACHE = {}

#return True after setting the data
def set(key, value):
    CACHE[key]=value
    return True

#return the value for key
def get(key):
    if key in CACHE.keys():
        return CACHE[key]
    return None

#delete key from the cache
def delete(key):
    del CACHE[key]

#clear the entire cache
def flush():
    CACHE.clear()

#print set('x', 1)
#>>> True

#print get('x')
#>>> 1

#print get('y')
#>>> None

#delete('x')
#print get('x')
#>>> None
