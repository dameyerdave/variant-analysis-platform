from rest_framework import viewsets
from core.helpers import parse_bool

class DefaultViewSet(viewsets.ModelViewSet):
    @classmethod
    def build(cls, **kwargs):
      """ Create a generic instance of FilterableViewSet"""
      class _DefaultViewSet(cls):
        model = kwargs['model']

        def get_serializer_class(self):
            if parse_bool(self.request.query_params.get('expand')) and 'serializer' in kwargs:
                serializer = kwargs['serializer']
            else:
                serializer = super().get_serializer_class()
            print('serializer', serializer)
            return serializer

        def get_queryset(self):
          qs = self.model.objects.filtered(self.request.query_params.get('filter'))
          if parse_bool(self.request.query_params.get('expand')) and 'prefetch_related' in kwargs:
              qs = qs.prefetch_related(*kwargs['prefetch_related'])

          return qs

      return _DefaultViewSet
