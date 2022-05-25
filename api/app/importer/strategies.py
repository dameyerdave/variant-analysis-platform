from django.db.utils import IntegrityError
from requests import RequestException
from importer.proxys import vep_offline, genenames
from django.utils.translation import gettext as _
from core.models import Evidence, Variant, Transcript, Gene, VariantConsequence, VariantEvidence
from django.db import transaction
from bioinfo_toolset.modules.formatter import transcript_name
from importer.evidence_providers import PubMedEvidenceProvider
from importer.proxys import vrs

class BaseStrategy():
    def import_one(self, params):
        raise NotImplementedError(f"You must implement import_one in the Strategy.")

class VepStrategy(BaseStrategy):
    def __init__(self):
        self.pubMedEvidenceProvider = PubMedEvidenceProvider()

    def _import_transcripts(self, variant, vep_info, params):
        """ Import the VEP transcripts and return the list of found transcripts """
        transcripts = []
        for transcript_consequence in vep_info.get('transcript_consequences'):
            # If transcript_id is a given parameter we filter out every other transcript
            if 'transcript_id' in params and params.get('transcript_id') and transcript_consequence.get('transcript_id').startswith(params.get('transcript_id')):
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
                symbol=transcript_consequence.get('gene_symbol') or transcript_consequence.get('gene_id'),
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
            if not found:
                _transcript_name = transcript_consequence.get(
                        'transcript_id')
            transcript, created = Transcript.objects.update_or_create(
                ensembl_id=transcript_consequence.get(
                    'transcript_id'),
                variant = variant,
                defaults={
                    'name': _transcript_name,
                    'hgvsg': transcript_consequence.get('hgvsg'),
                    'hgvsc': transcript_consequence.get('hgvsc'),
                    'hgvsp': transcript_consequence.get('hgvsp'),
                    'gene': gene,
                    'annotations': transcript_consequence
                }
            )
            transcripts.append(transcript)
        return transcripts


    def _import_pubmed_evidences(self, vep_info, variant):
        if 'colocated_variants' in vep_info:
            for colocated_variant in vep_info.get('colocated_variants'):
                if 'pubmed' in colocated_variant:
                    for pmid in colocated_variant.get('pubmed'):
                        _evidence = self.pubMedEvidenceProvider.fetch(pmid=pmid)
                        if _evidence:
                            try:
                                evidence, created = Evidence.objects.update_or_create(
                                    reference=_evidence.get('reference'),
                                    source=_evidence.get('source'),
                                    defaults={
                                        'title': _evidence.get('title'),
                                        'summary': _evidence.get('summary'),
                                        'evidence_date': _evidence.get('evidence_date')
                                    }
                                )
                                variant_evidence, created = VariantEvidence.objects.get_or_create(
                                    variant=variant,
                                    evidence=evidence
                                )
                            except IntegrityError:
                                pass

    def _import_variant(self, vep_info, params):
        annotations = self.__extract_variant_annotations(vep_info)
        if params.get('annotations'):
            annotations.update(params.get('annotations'))
        variant, _ = Variant.objects.update_or_create(
                assembly=vep_info.get('assembly_name'),
                chromosome=vep_info.get('seq_region_name'),
                start=vep_info.get('start'),
                end=vep_info.get('end'),
                allele_string=vep_info.get('allele_string'),
                defaults={
                    'strand': vep_info.get('strand'),
                    'variant_class': vep_info.get('variant_class'),
                    'vrs_id': vrs(vep_info),
                    'most_severe_consequence': VariantConsequence.objects.get(term=vep_info.get('most_severe_consequence')),
                    'annotations': annotations
                }
            )
        return variant


    def _get_vep_info(self, params):
        vep_resp = vep_offline(f"{params['chr']}_{params['start']}{'_' + params['end'] if 'end' in params and params['end'] else ''}_{params['ref']}_{params['alt']}", **params['vep_options'])
        if vep_resp.ok:
            vep_info = vep_resp.json()[0]
            return vep_info
        else:
            raise RequestException(vep_resp.json())


    def import_one(self, params):
        variant = None
        with transaction.atomic():
            vep_info = self._get_vep_info(params)
            variant = self._import_variant(vep_info, params)
            self._import_transcripts(variant, vep_info, params)
            self._import_pubmed_evidences(vep_info, variant)
        return variant
        
    def __extract_variant_annotations(self, vep_info):
        variant_annotations = {}
        if 'colocated_variants' in vep_info:
            for colocated_variant in vep_info.get('colocated_variants'):
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
        if 'regulatory_feature_consequences' in vep_info:
            variant_annotations['regulatory_feature_conequences'] = vep_info.get('regulatory_feature_consequences')
        return variant_annotations