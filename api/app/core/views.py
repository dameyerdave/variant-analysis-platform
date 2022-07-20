from rest_framework import viewsets
from rest_framework import views
from django import views as django_views
from core.helpers import parse_bool
from django.db.models import Prefetch
from config.config import Config
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
import xhtml2pdf.pisa as pisa
from io import BytesIO
import base64
from django.utils.translation import gettext as _

from core.models import Gene, Sample, Transcript, Variant

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
          
          # Get filtered queryset
          _filter = self.request.query_params.get('filter', None)
          ordering = config.get_ordering(self.model.__name__.lower())
          qs = self.model.objects.filtered(_filter, ordering)
          
          # Expand
          if parse_bool(self.request.query_params.get('expand')):
              if 'prefetch' in kwargs:
                prefetches = []
                for prefetch in kwargs['prefetch']:
                  prefetches.append(self.__get_prefetch(prefetch, _filter))
                qs = qs.prefetch_related(*prefetches)
              if 'related' in kwargs:
                qs = qs.select_related(*kwargs['related'])

          # Run the individual queryset_extra function
          if 'queryset_extra' in kwargs:
              # If there is a queryset_extra function we run this before returning it
              qs = kwargs['queryset_extra'](qs, _filter)

          return qs

      return _DefaultViewSet

class ReportView(django_views.View):
  def get(self, request, format, **kwargs):
    template = get_template('default_report.html')
    html = template.render({'format': format}, request)
    if format == 'pdf':
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
          return HttpResponse(response.getvalue(), content_type='application/pdf')
    elif format == 'base64':
        return HttpResponse(base64.b64encode(html.encode('utf-8')), content_type='text/plain')
    else:
      return HttpResponse(html)

class StatisticsView(views.APIView):
  def get(self, request, **kwargs):
    stats = {
      'counts': {
        'samples': Sample.objects.count(),
        'variants': Variant.objects.count(),
        'transcripts': Transcript.objects.count(),
        'genes': Gene.objects.count(),
      }
    }
    return JsonResponse(stats)
