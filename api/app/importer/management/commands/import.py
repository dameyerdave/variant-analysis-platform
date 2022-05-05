from django.core.management.base import BaseCommand
from config.config import Config
from importer.parsers import TsvParser
from importer.strategies import VepStrategy
import re
import logging
from os.path import join
import traceback
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    parser_map = {
      'tsv': TsvParser
    }
    strategy_map = {
      'vep': VepStrategy
    }

    def add_arguments(self, parser):
        parser.add_argument('config', type=str, help='The config to use to import the file')
        parser.add_argument('file', type=str, help='The file to import')
        parser.add_argument('--one', action='store_true', help='Only import the first row (for testing purposes)')
        parser.add_argument('--sample-id', type=str, help='The sample id')

    def __extract_value(self, row, config):
        if not config:
            return None
        field = config.get('field')
        regex = config.get('regex')

        if field:
            value = row[field]
            if regex:
                match = re.match(regex, value)
                if match:
                    return match.group(1)
            else:
              return value
        return None

    def __get_allele(self, allele, strand):
        if not allele:
            return allele
        inverse = {
          'A': 'T',
          'T': 'A',
          'G': 'C',
          'C': 'G'
        }
        if strand in ['-']:
            return inverse[allele]
        return allele

    def __dynamic_strategy(self, _strategy):
        if _strategy and _strategy in self.strategy_map:
            return self.strategy_map[_strategy]()
        else:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location('modules.importer', join('..', 'modules', 'importer', f"{_strategy}.py"))
                importer_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(importer_module)
                return importer_module.ImportStrategy()
            except ImportError as ie:
                self.stdout.write(self.style.ERROR(f"importer module {_strategy} not found."))
                raise ie
        

    def handle(self, *args, **options):
      try:
        config = Config()
        import_config = config.get_import_config(options['config'])
        if not import_config:
            self.stdout.write(self.style.ERROR(f"Config {config} not defined."))
        try:
            parser = self.parser_map[import_config.get('format', 'tsv')]()
            strategy = self.__dynamic_strategy(import_config.get('strategy', 'vep'))
            for row in parser.parse(options['file']):
                strand = self.__extract_value(row, import_config.get('strand'))
                # The parameters of a variant are chr, start, end, ref, alt
                # Optional a transcript ID could be provided to be more specific
                # as data the row is provided
                params = {
                  'config': import_config, 
                  'chr': self.__extract_value(row, import_config.get('chromosome')),
                  'start': self.__extract_value(row, import_config.get('start')),
                  'end': self.__extract_value(row, import_config.get('end')),
                  'ref': self.__get_allele(self.__extract_value(row, import_config.get('ref')), strand),
                  'alt': self.__get_allele(self.__extract_value(row, import_config.get('alt')), strand),
                  'transcript_id': self.__extract_value(row, import_config.get('transcript_id')),
                  'data': row,
                  'sample_id': options.get('sample_id')
                }

                # Check if the required keys are given
                check = True
                for key in ['chr', 'start', 'ref', 'alt']:
                    if params[key] is None:
                        check = False
                        break
                        
                if check:
                    # self.stdout.write(f"Import variant: {params}")
                    imported, _ = strategy.import_one(params)
                    if imported:
                        self.stdout.write(self.style.SUCCESS("Imported variant: {chr}:{start}{ref}>{alt}".format(**params)))
                    else:
                        self.stdout.write(self.style.ERROR("Variant could not be imported: {chr}:{start}{ref}>{alt}".format(**params)))
                else:
                    self.stdout.write(self.style.ERROR("Variant definition not sufficient: {chr}:{start}{ref}>{alt}".format(**params)))    

                if options.get('one'):
                    break
                
        except FileNotFoundError as fnf:
            self.stdout.write(self.style.ERROR(fnf))
      except Exception as ex:
        self.stdout.write(self.style.ERROR(ex))
        traceback.print_exc()