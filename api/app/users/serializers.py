from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_otp import match_token
from rest_framework import serializers
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        read_only=True, slug_field='name', many=True)

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'groups'
        )


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
