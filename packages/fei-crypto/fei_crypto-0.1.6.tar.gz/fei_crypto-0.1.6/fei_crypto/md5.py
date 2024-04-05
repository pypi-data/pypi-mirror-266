import hashlib
import json


def md5(obj:object):
    return hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()


