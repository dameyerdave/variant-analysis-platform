from rest_framework import viewsets
from core.helpers import parse_bool
from django.db.models import Prefetch
from config.config import Config

class DefaultViewSet(viewsets.ModelViewSet):
    @classmethod
    def build(cls, **kwargs):
      """ 
      Create a generic instance of DefaultViewSet

      This applies filters and take care of the expand query parameter.
      """
      class _DefaultViewSet(cls):
        model = kwargs['model']

        def get_serializer_class(self):
          """ Returns ether the default serializer or the expanded one based on the 'expand' query parameter """
          if parse_bool(self.request.query_params.get('expand')) and 'expand_serializer' in kwargs:
              serializer = kwargs['expand_serializer']
          else:
              serializer = super().get_serializer_class()
          return serializer

        def __get_prefetch(self, prefetch, _filter):
          """ 
          Returns a Prefetch object based on the prefetch definition.

          A special thing here is that we can encapsulate prefetches, therefore
          we need to use recursion.
          """
          if 'prefetch' in prefetch:
              return Prefetch(prefetch['property'], prefetch['model'].objects.filtered(_filter).prefetch_related(self.__get_prefetch(prefetch['prefetch'], _filter)))
          else:
              return Prefetch(prefetch['property'], prefetch['model'].objects.filtered(_filter))

        def get_queryset(self):
          """ Returns a queryset based on the filter and the prefetch definition. """
          config = Config()
          _filter = self.request.query_params.get('filter', 'default')
          qs = self.model.objects.filtered(_filter)
          if parse_bool(self.request.query_params.get('expand')):
              if 'prefetch' in kwargs:
                prefetches = []
                for prefetch in kwargs['prefetch']:
                  prefetches.append(self.__get_prefetch(prefetch, _filter))
                qs = qs.prefetch_related(*prefetches)
              if 'related' in kwargs:
                qs = qs.select_related(*kwargs['related'])
          if 'queryset_extra' in kwargs:
              # If there is a queryset_extra function we run this before returning it
              qs = kwargs['queryset_extra'](qs, _filter)
          ordering = config.get_ordering(self.model.__name__.lower())
          if ordering:
            qs = qs.order_by(*ordering)
          return qs

      return _DefaultViewSet
