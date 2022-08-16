from uuid import uuid4
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _
from django_otp.plugins.otp_totp.models import TOTPDevice
from uuid import uuid4
from emailer import Emailer


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def __createOTPDevice(self, user):
        print('__createOTPDevice')
        TOTPDevice.objects.create(
            user=user,
            name=uuid4().hex,
            confirmed=True
        )

    def __sendOTPEmail(self, user):
        # Send an email including the qrcode to the user
        Emailer.send_using_template(_('Your OPT token'), (user.email,),
                                    'users/default_otp_token.html', {'user': user.context, 'qrcode': user.otp_qrcode_base64()})

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        # For each user we create ONE OTP device
        self.__createOTPDevice(user)

        # We send an Email to the user with the OTP QR code
        self.__sendOTPEmail(user)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
