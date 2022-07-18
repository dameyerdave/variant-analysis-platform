from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_otp import match_token
from rest_framework import serializers
from django.utils.translation import gettext as _


class TokenObtainPair2FASerializer(TokenObtainPairSerializer):
  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["token"] = serializers.IntegerField()

  def validate(self, attrs):
    data = super().validate(attrs)
    print('data', data)
    token = attrs['token']
    if match_token(self.user, token):
      return data
    else:
      error = {'detail': _('2FA token invalid')}
      raise serializers.ValidationError(error)

