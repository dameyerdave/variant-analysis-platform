import redis
import pickle
import requests
import json
from hashlib import md5
from os import environ

class RedisCache():
  def __init__(self):
      self.cache = redis.Redis(
        host=environ.get('REDIS_HOST', 'redis'), 
        port=int(environ.get('REDIS_PORT', 6379)), 
        db=0
      )
  def get(self, req, **params):
      to_hash = {
        'req': req,
        'params': params
      }
      _hash = md5(json.dumps(to_hash, sort_keys=True).encode('utf-8')).hexdigest()
      if self.cache.exists(_hash):
        return pickle.loads(self.cache.get(_hash))
      else:
        resp = requests.get(req, **params)
        self.cache.set(_hash, pickle.dumps(resp))
        return resp