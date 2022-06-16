from django.core.management.base import BaseCommand
from config.config import Config
from importer.parsers import TsvParser
from importer.strategies import VepStrategy
import re
from os.path import join
import traceback
from friendlylog import colored_logger as log


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
        parser.add_argument('--assembly', type=str, help='The assembly to use [GRCh38, GRCh37]')
        parser.add_argument('--one', action='store_true', help='Only import the first row (for testing purposes)')
        parser.add_argument('--sample', type=str, help='The sample id')
        

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
                spec = importlib.util.spec_from_file_location('plugins.importer', join('..', 'plugins', 'importer', f"{_strategy}.py"))
                importer_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(importer_module)
                return importer_module.ImportStrategy()
            except ImportError as ie:
                log.error(f"importer plugin {_strategy} not found.")
                raise ie
        

    def handle(self, *args, **options):
      try:
        config = Config()
        import_config = config.get_import_config(options['config'])
        if not import_config:
            log.error(f"Config {config} not defined.")
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
                  'sample': self.__extract_value(row, import_config.get('sample')) or options.get('sample'),
                  'chr': self.__extract_value(row, import_config.get('chromosome')),
                  'start': self.__extract_value(row, import_config.get('start')),
                  'end': self.__extract_value(row, import_config.get('end')),
                  'ref': self.__get_allele(self.__extract_value(row, import_config.get('ref')), strand),
                  'alt': self.__get_allele(self.__extract_value(row, import_config.get('alt')), strand),
                  'transcript_id': self.__extract_value(row, import_config.get('transcript_id')),
                  'data': row,
                  'vep_options': {
                      'assembly': options.get('assembly') or import_config.get('assembly')
                  }
                }

                # Check if the required keys are given
                check = True
                for key in ['chr', 'start', 'ref', 'alt']:
                    if params[key] is None:
                        check = False
                        break
                        
                if check:
                    # log.debug(f"Import variant: {params}")
                    variant = strategy.import_one(params)
                    if variant:
                        log.info("Imported variant: {chr}:{start}{ref}>{alt}".format(**params))
                    else:
                        log.error("Variant could not be imported: {chr}:{start}{ref}>{alt}".format(**params))
                else:
                    log.error("Variant definition not sufficient: {chr}:{start}{ref}>{alt}".format(**params))

                if options.get('one'):
                    break
                
        except FileNotFoundError as fnf:
            log.error(fnf)
      except Exception as ex:
        log.error(ex)
        traceback.print_exc()