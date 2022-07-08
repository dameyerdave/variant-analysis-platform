from django.db.utils import IntegrityError
from requests import RequestException
from importer.proxys import vep_offline, genenames
from django.utils.translation import gettext as _
from core.models import (Disease, Evidence, Phenotype, Variant, Transcript, Gene, VariantConsequence, 
                        VariantDisease, VariantEvidence, Sample, SampleVariant, DiseaseDiseaseClass, 
                        DiseaseClass, DiseaseEvidence)
from django.db import transaction
from bioinfo_toolset.modules.formatter import transcript_name
from importer.evidence_providers import PubMedEvidenceProvider
from importer.proxys import vrs, gnomad, omim, disgenet
from config.config import Config
from friendlylog import colored_logger as log
from importer.decorators import time

class BaseStrategy():
    def import_one(self, params):
        raise NotImplementedError(f"You must implement import_one in the Strategy.")

class VepStrategy(BaseStrategy):
    def __init__(self):
        self.pubMedEvidenceProvider = PubMedEvidenceProvider()
        self.config = Config().get_import_config('general')

    @time('Import transcripts')
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
                omim_resp = omim(transcript_consequence.get('gene_symbol'))
                if omim_resp.ok:
                    omim_info = omim_resp.json()
                    for geneMap in omim_info['omim']['searchResponse']['geneMapList']:
                        geneMap = geneMap['geneMap']
                        if 'phenotypeMapList' in geneMap:
                            for phenotypeMap in geneMap['phenotypeMapList']:
                                phenotypeMap = phenotypeMap['phenotypeMap']
                                ims = []
                                if phenotypeMap['phenotypeInheritance']:
                                    ims = phenotypeMap['phenotypeInheritance'].split(';')
                                phenotype = Phenotype.objects.update_or_create(
                                    gene = gene,
                                    phenotype = phenotypeMap['phenotype'],
                                    defaults = {
                                        'inheritance_modes': ims,
                                        'annotations': phenotypeMap
                                    }
                                )
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

    def _add_pubmed_evidence(self, pmid, variant, disease=None):
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
                # If there is a disease to link we add a disease evidence
                if disease:
                    disease_evidence, created = DiseaseEvidence.objects.get_or_create(
                        disease=disease,
                        evidence=evidence
                    )
            except IntegrityError:
                pass

    @time('Import pubmed evidences')
    def _import_pubmed_evidences(self, vep_info, variant):
        if self.config['sources']['pubmed'] == False:
            return
        if 'colocated_variants' in vep_info:
            for colocated_variant in vep_info.get('colocated_variants'):
                if 'pubmed' in colocated_variant:
                    for pmid in colocated_variant.get('pubmed'):
                        self._add_pubmed_evidence(pmid, variant)

    @time('Import variant')
    def _import_variant(self, vep_info, params):
        annotations = self.__extract_variant_annotations(vep_info)
        # print('most_severe_consequence', vep_info.get('most_severe_consequence'))
        if params.get('annotations'):
            annotations.update(params.get('annotations'))
        variant, _ = Variant.objects.update_or_create(
                assembly=vep_info.get('assembly_name'),
                chromosome=vep_info.get('seq_region_name'),
                start=vep_info.get('start'),
                end=vep_info.get('end'),
                allele_string=vep_info.get('allele_string'),
                dbsnp_id=self.__extract_dbsnp_id(annotations),
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

    @time('Import gnomad')
    def _import_gnomad(self, vep_info):
        if self.config['sources']['gnomad'] == False:
            return
        ref, alt = vep_info.get('allele_string').split('/')
        resp = gnomad(f"{vep_info.get('seq_region_name')}-{vep_info.get('start')}-{ref}-{alt}", assembly=vep_info.get('assembly_name'))
        maf = None
        clinvar_submissions = None
        if resp.ok:
            data = resp.json()
            if 'data' in data and 'variant' in data['data'] and data['data']['variant'] and 'genome' in data['data']['variant']:
                maf = data['data']['variant']['genome']
            if 'data' in data and 'clinvar_variant' in data['data'] and data['data']['clinvar_variant'] and 'submissions' in data['data']['clinvar_variant']:
                clinvar_submissions = data['data']['clinvar_variant']['submissions']
        
        return {'maf': maf, 'clinvar_submissions': clinvar_submissions}

    @time('Import sample')
    def _import_sample(self, params, variant):
        if params.get('sample'):
            sample, _ = Sample.objects.get_or_create(id=params.get('sample'))
            SampleVariant.objects.get_or_create(
                sample=sample,
                variant=variant,
                zygosity=params.get('zygosity')
            )

    @time('Import disgenet')
    def _import_disgenet(self, variant):
        if self.config['sources']['disgenet'] == False:
            return
        if variant.dbsnp_id:
            resp = disgenet(variant.dbsnp_id)
            if resp.ok:
                disgenet_info = resp.json()
                for disease_info in disgenet_info.get('diseases'):
                    disease, _ = Disease.objects.update_or_create(
                        identifier = disease_info.get('diseaseid'),
                        defaults = {
                            'name': disease_info.get('disease_name'),
                            'type': disease_info.get('disease_type'),
                            # 'semantic_type': disgenet_info.get('disease_semantic_type'),
                            'annotations': disease_info
                        }    
                    )
                    if disease_info.get('disease_class'):
                        for idx, identifier in enumerate(disease_info.get('disease_class')):
                            disease_class, _ = DiseaseClass.objects.update_or_create(
                                identifier = identifier,
                                name = disease_info.get('disease_class_name')[idx]
                            )
                            DiseaseDiseaseClass.objects.get_or_create(
                                disease = disease,
                                disease_class = disease_class
                            )
                    VariantDisease.objects.get_or_create(
                        variant=variant,
                        disease=disease
                    )
                    # Import all the evidences provided by disgenet
                    for evidence in disease_info.get('evidences'):
                        if evidence.get('pmid'):
                            self._add_pubmed_evidence(evidence.get('pmid'), variant, disease)

    @time('Import one variant')
    def import_one(self, params):
        variant = None
        vep_info = self._get_vep_info(params)
        annotations = self._import_gnomad(vep_info)
        params.update({
            'annotations': annotations
        })
        with transaction.atomic():    
            variant = self._import_variant(vep_info, params)
            self._import_transcripts(variant, vep_info, params)
            self._import_sample(params, variant)
            self._import_pubmed_evidences(vep_info, variant)
            self._import_disgenet(variant)
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

    def __extract_dbsnp_id(self, annotations):
        if 'id' in annotations:
            ids = annotations.get('id')
            if isinstance(ids, str):
                ids = [ids]
            for id in annotations.get('id'):
                if id.startswith('rs'):
                    return id
        return None
