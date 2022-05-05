from importer.proxys import vep_offline, genenames
from django.utils.translation import gettext as _
from core.models import Variant, Transcript, Gene, VariantConsequence
from django.db import transaction
from bioinfo_toolset.modules.formatter import transcript_name
from config.config import Config

class BaseStrategy():
    def import_one(self, params):
        raise NotImplementedError(f"You must implement import_one in the Strategy.")

class VepStrategy(BaseStrategy):
    def import_one(self, params):
        vep_resp = vep_offline(f"{params['chr']}_{params['start']}{'_' + params['end'] if 'end' in params and params['end'] else ''}_{params['ref']}_{params['alt']}")
        # print('vep_resp', vep_resp.json())
        if vep_resp.ok:
            vep_info = vep_resp.json()[0]
            with transaction.atomic():
                variant, _ = Variant.objects.update_or_create(
                    assembly=vep_info.get('assembly_name'),
                    chromosome=vep_info.get('seq_region_name'),
                    start=vep_info.get('start'),
                    end=vep_info.get('end'),
                    allele_string=vep_info.get('allele_string'),
                    strand=vep_info.get('strand'),
                    variant_type='SNV',
                    defaults={
                        'most_severe_consequence': VariantConsequence.objects.get(term=vep_info.get('most_severe_consequence')),
                        'annotations': self.__extract_variant_annotations(vep_info.get('colocated_variants'))
                    }
                )
                for transcript_consequence in vep_info.get('transcript_consequences'):
                    # If transcript_id is a given parameter we filter out every other transcript
                    if 'transcript_id' in params and not transcript_consequence.get('transcript_id').startswith(params['transcript_id']):
                        continue
                    # If canonical is given we filter out all non canonical transcirpts
                    if 'canonical' in params and params['canonical'] and not transcript_consequence.get('canonical'):
                        continue
                    # If pick is given we filter out all non picked transcirpts
                    if 'pick' in params and params['pick'] and not transcript_consequence.get('pick'):
                        continue
                    if transcript_consequence.get('source') == 'Ensembl':
                        gene_defaults = {
                            'ensembl_id': transcript_consequence.get('gene_id')
                        }
                    elif transcript_consequence.get('source') == 'RefSeq':
                        gene_defaults = {
                            'entrez_id': transcript_consequence.get('gene_id')
                        }
                    gene, created = Gene.objects.update_or_create(
                        symbol=transcript_consequence.get('gene_symbol'),
                        defaults = gene_defaults
                    )
                    if created:
                        genenames_resp = genenames(
                            transcript_consequence.get('gene_symbol'))
                        if genenames_resp.ok:
                            gene_info = genenames_resp.json()
                            if len(gene_info['response']['docs']) > 0:
                                gene.annotations = gene_info['response']['docs'][0]
                                gene.save()
                    _transcript_name, found = transcript_name(
                        transcript_consequence)
                    if found:
                        transcript, created = Transcript.objects.update_or_create(
                            ensembl_id=transcript_consequence.get(
                                'transcript_id'),
                            defaults={
                                'name': _transcript_name,
                                'hgvsc': transcript_consequence.get('hgvsc'),
                                'hgvsp': transcript_consequence.get('hgvsp'),
                                'gene': gene,
                                'variant': variant,
                                'annotations': transcript_consequence
                            }

                        )
                        # if created:
                        #     for hgvs in (transcript.hgvsc, transcript.hgvsp):
                        #         alleleregistry_resp = alleleregistry(hgvs)
                        #         if alleleregistry_resp.ok:
                        #             alleleregistry_info = alleleregistry_resp.json()
                        #             AlleleRegistry.objects.get_or_create(
                        #                 hgvs=hgvs,
                        #                 annotations=alleleregistry_info
                        #             )
            return True, vep_info
        else:
            return False, vep_resp.json()

    def __extract_variant_annotations(self, colocated_variants):
        variant_annotations = {}
        if colocated_variants:
            for colocated_variant in colocated_variants:
                for key, value in colocated_variant.items():
                    if key in variant_annotations:
                        if not isinstance(variant_annotations[key], list):
                            variant_annotations[key] = [variant_annotations[key], value]
                        else:
                            # print('variant_annotations', key, value, variant_annotations)
                            variant_annotations[key].append(value)
                    else:
                        variant_annotations[key] = value 
            # cleanup: we create a uniq set of values and if there
            # is only one value we assign this one directly
            for key, value in variant_annotations.items():
                if isinstance(value, list):
                    try:
                        value = list(set(value))
                        if len(value) == 1:
                            value = value[0]
                        variant_annotations[key] = value
                    except TypeError:
                        # we ignore type errors in case the list contains dicts
                        pass
        return variant_annotations