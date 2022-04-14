from django.db.models import Q

def q_or_list(predicates, query, op=None):
  ret = Q()
  for predicate in predicates:
    if op:
      ret |= Q(**{f"{predicate}__{op}": query})
    else:
      ret |= Q(**{f"{predicate}": query})
  return ret

def q_from_config(config):
  ret = Q()
  if isinstance(config, dict):
    if list(config.keys())[0] == 'and':
      if isinstance(config['and'], list):
        for statement in config['and']:
          ret &= q_from_config(statement)
    elif list(config.keys())[0] == 'or':
      if isinstance(config['or'], list):
        for statement in config['or']:
          ret |= q_from_config(statement)
    else:
      predicate, value = list(config.items())[0]
      return Q(**{f"{predicate}": value})
  return ret

def parse_bool(value):
  if value is None:
      return False
  return value.lower() == 'true' or value == '1' or value.lower() == 't'
  
