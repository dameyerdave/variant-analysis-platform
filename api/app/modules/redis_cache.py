import traceback
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

  def __query(self, method, req, **params):
      ignore_cache = params.get('ignore_cache')
      if not ignore_cache:
          to_hash = {
            'req': req,
            'params': params
          }
          _hash = md5(json.dumps(to_hash, sort_keys=True).encode('utf-8')).hexdigest()
          if self.cache.exists(_hash):
              return pickle.loads(self.cache.get(_hash))
      if 'ignore_cache' in params:
          del params['ignore_cache']
      
      try:
          if method == 'POST':
            resp = requests.post(req, **params)
          elif method == 'GET':
            resp = requests.get(req, **params)
          else:
            raise Exception(f"Method {method} not supported.")
      except Exception as ex:
          traceback.print_exc()
          raise ex
      
      if not ignore_cache:
          self.cache.set(_hash, pickle.dumps(resp))
      return resp
  
  def get(self, req, **params):
      return self.__query('GET', req, **params)    
  
  def post(self, req, **params):
      return self.__query('POST', req, **params)