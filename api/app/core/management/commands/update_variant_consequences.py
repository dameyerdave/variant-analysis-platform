from hashlib import new
from django.core.management.base import BaseCommand
from django.core.management import call_command
import traceback
from friendlylog import colored_logger as log
import yaml
import requests
from os.path import join


class Command(BaseCommand):
    def __get_impact(self, cons, consequence_ranking):
        """ calculate the impact based on already known impacts based on the range of the consequence_ranking """
        impacts = list(set([item['fields']['impact'] for item in cons]))
        ranges = {}
        for impact in impacts:
            useful_cons = list(filter(lambda x:x['fields']['impact'] == impact and 'consequence_ranking' in x['fields'], cons))
            ranks = [item['fields']['consequence_ranking'] for item in sorted(useful_cons, key=lambda x:x['fields']['consequence_ranking'])]
            ranges[impact] = [ranks[0], ranks[-1]]

        for impact, range in ranges.items():
            if range[0] <= consequence_ranking <= range[1]:
                return impact
        return 'MODIFIER'


    def handle(self, *args, **options):
      """ 
      updated the variant consequences from ensembl
      IMPORTANT: The pk must stay the same over all time for the same consequence!
      """
      try:
        resp = requests.get('https://rest.ensembl.org/info/variation/consequence_types?content-type=application/json&rank=1')
        if resp.ok:
          vep_var_cons = resp.json()
          with open(join('core', 'fixtures','variant_consequences.yaml'), 'r') as var_cons_file:
            old_var_cons = yaml.load(var_cons_file, Loader=yaml.FullLoader)
          new_var_cons = []
          next_pk = max(old_var_cons, key=lambda x:x['pk']).get('pk') + 1
          for vep_var_con in vep_var_cons:
              old_var_con = next((item for item in old_var_cons if item['fields']['term'] == vep_var_con.get('SO_term')), None)
              if old_var_con:
                  log.info(f"Updating consequence: {vep_var_con.get('SO_term')}")
                  new_var_cons.append({
                    'model': 'core.variantconsequence',
                    'pk': old_var_con['pk'],
                    'fields': {
                      'term': vep_var_con.get('SO_term'),
                      'hr_term': vep_var_con.get('label'),
                      'impact': old_var_con['fields']['impact'],
                      'description': vep_var_con.get('description'),
                      'accession': vep_var_con.get('SO_accession'),
                      'consequence_ranking': int(vep_var_con.get('consequence_ranking'))
                    }
                  })
              else:
                  log.info(f"Adding new consequence: {vep_var_con.get('SO_term')}")
                  new_var_cons.append({
                    'model': 'core.variantconsequence',
                    'pk': next_pk,
                    'fields': {
                      'term': vep_var_con.get('SO_term'),
                      'hr_term': vep_var_con.get('label'),
                      'impact': self.__get_impact(old_var_cons, int(vep_var_con.get('consequence_ranking'))),
                      'description': vep_var_con.get('description'),
                      'accession': vep_var_con.get('SO_accession'),
                      'consequence_ranking': int(vep_var_con.get('consequence_ranking'))
                    }
                  })
                  next_pk += 1
          with open(join('core', 'fixtures','variant_consequences.yaml'), 'w') as var_cons_file:
            yaml.dump(sorted(new_var_cons, key=lambda x:x['pk']), var_cons_file)

          call_command('loaddata', 'variant_consequences')
      except Exception as ex:
        log.error(ex)
        traceback.print_exc()