from django.db.models import Q

def q_or_list(predicates, query, op=None):
  ret = Q()
  for predicate in predicates:
    if op:
      ret |= Q(**{f"{predicate}__{op}": query})
    else:
      ret |= Q(**{f"{predicate}": query})
  return ret