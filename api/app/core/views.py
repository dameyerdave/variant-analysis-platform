from django import views
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.helpers import parse_bool
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
from config.config import Config
from django.template.loader import get_template
from django.http import HttpResponse
import xhtml2pdf.pisa as pisa
from io import BytesIO
import base64
import json
import traceback
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from users.managers import CustomUserManager

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

class Report(views.View):
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

class OtpToken(views.View):
  def get(self, request, **kwargs):
    template = get_template('default_otp_token.html')
    ctx = {
      
    }
    html = template.render(ctx, request)
    return HttpResponse(base64.b64encode(html.encode('utf-8')), content_type='text/plain')
    

class UserViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def me(self, request):
        user = get_user_model().objects.get(id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def otp_token(self, request):
        user = get_user_model().objects.get(id=request.user.id)
        qr_code = user.otp_qrcode()
        response = HttpResponse(content_type="image/png")
        qr_code.save(response)
        return response

    @action(detail=False, methods=['post'])
    def register(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
          user = get_user_model().objects.create_user(data.get('email'), data.get('password'), **{
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name')
          })
        except IntegrityError as ie:
          return Response({'detail': _('User {} already exists').format(data.get('email'))}, status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as ex:
          traceback.print_exc()
          return Response({'detail': str(ex)}, status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_201_CREATED)
