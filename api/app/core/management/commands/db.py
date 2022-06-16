from django.core.management.base import BaseCommand
from django.core.management import call_command
import traceback
from friendlylog import colored_logger as log


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help='The action to execute')
        
    def init(self):
        call_command('loaddata', 'variant_consequences')

    def clean(self):
        call_command('flush')
        call_command('makemigrations', 'core')
        call_command('migrate')
        self.init()

    def handle(self, *args, **options):
      try:
        if options.get('action') == 'clean':
          self.clean()
        elif options.get('action') == 'init':
          self.init()
      except Exception as ex:
        log.error(ex)
        traceback.print_exc()
