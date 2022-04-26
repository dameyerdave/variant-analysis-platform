from django.db.models import Q, Aggregate, CharField, Value

def q_or_list(predicates, query, op=None):
  ret = Q()
  for predicate in predicates:
    if op:
      ret |= Q(**{f"{predicate}__{op}": query})
    else:
      ret |= Q(**{f"{predicate}": query})
  return ret

def q_from_config(config, prefix: str = ''):
  ret = Q()
  if isinstance(config, dict):
    if list(config.keys())[0] == 'and':
      if isinstance(config['and'], list):
        for statement in config['and']:
          ret &= q_from_config(statement, prefix)
    elif list(config.keys())[0] == 'or':
      if isinstance(config['or'], list):
        for statement in config['or']:
          ret |= q_from_config(statement, prefix)
    else:
      predicate, value = list(config.items())[0]
      return Q(**{f"{prefix}{predicate}": value})
  return ret

def parse_bool(value):
  if value is None:
      return False
  return value.lower() == 'true' or value == '1' or value.lower() == 't'
  
class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(expressions)s)'

    def __init__(self, expression, delimiter, **extra):
        output_field = extra.pop('output_field', CharField())
        delimiter = Value(delimiter)
        super(GroupConcat, self).__init__(
            expression, delimiter, output_field=output_field, **extra)

    def as_postgresql(self, compiler, connection):
        self.function = 'STRING_AGG'
        return super(GroupConcat, self).as_sql(compiler, connection)