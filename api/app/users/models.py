from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from django.utils.http import urlencode
from users.managers import CustomUserManager
import qrcode
import base64
import io


class User(AbstractUser):
    # Remove the username field
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def context(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

    def otp_qrcode_value(self):
        device = self.totpdevice_set.first()
        return device.config_url

    def otp_qrcode(self):
        code = qrcode.QRCode()
        code.add_data(self.otp_qrcode_value())
        return code

    def otp_qrcode_base64(self):
        code = self.otp_qrcode()
        img = code.make_image()
        buffer = io.BytesIO()
        img.save(buffer)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @property
    def group_list(self):
        return self.groups.values_list('name', flat=True)

    # Permission related methods
    def is_in_any_group(self, groups):
        return any(group in groups for group in self.group_list)

    class Meta:
        db_table = 'auth_user'
