from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.utils.html import strip_tags

class Emailer():
  def send_using_template(self, subject, to_emails, template, context):
    html_message = render_to_string(template, context)
    self.send(subject, to_emails, html_message)

  def send(self, subject, to_emails, html_message):
    send_mail(
      subject,
      strip_tags(html_message),
      settings.EMAIL_FROM,
      to_emails,
      html_message=html_message
  )