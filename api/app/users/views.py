from django import views
from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.http import HttpResponse
import base64
import json
import traceback
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from users.serializers import UserSerializer
from users.permissions import IsOwnUser


class OtpToken(views.View):
    def get(self, request, **kwargs):
        template = get_template('users/default_otp_token.html')
        ctx = {

        }
        html = template.render(ctx, request)
        return HttpResponse(base64.b64encode(html.encode('utf-8')), content_type='text/plain')


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnUser,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

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

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            user = get_user_model().objects.get(id=request.user.id)
            if user.check_password(data.get('password')):
                try:
                    validate_password(data.get('new_password'))
                    user.set_password(data.get('new_password'))
                    user.save()
                except ValidationError as ve:
                    return Response({'detail': ve}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': _('Password is not correct.')}, status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            traceback.print_exc()
            return Response({'detail': str(ex)}, status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)
