from django.test import TestCase
from emailer import Emailer
from django.conf import settings
from django.contrib.auth import get_user_model
from os import environ

class EmailerTest(TestCase):
  def setUp(self):
    self.user = get_user_model().objects.create_user(email=environ.get('DJANGO_SU_EMAIL'), password='secret')

  def test_emailer(self):
    """ Test sending email to admin with it's qr code"""
    Emailer.send_using_template('test email', (self.user.email,), 'default_otp_token.html', {'qrcode': self.user.otp_qrcode_base64()})
