from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from os import environ
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        superuser = environ.get('DJANGO_SU_EMAIL', 'admin@admin.com')
        user = get_user_model().objects.get(email=superuser)
        qrcode = user.otp_qrcode()
        qrcode.print_ascii(tty=True)
