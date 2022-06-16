from importer.strategies import VepStrategy
from importer.helpers import Field
from core.models import Sample, SampleVariant, Variant, Gene, Transcript, VariantConsequence
from django.db import transaction
from importer.proxys import vep_offline, genenames
from bioinfo_toolset.modules.formatter import transcript_name
from friendlylog import colored_logger as log
from importer.proxys import vrs


class ImportStrategy(VepStrategy):
    def import_one(self, params):
        config = params.get('config')
        data = params.get('data')
        variant = None
        if data:
            params.update({
                'vep_options': {
                    'assembly': 'GRCh38'
                },
                'zygosity': data.get('Zygosity').split(':')[0]
            })
            vep_info = self._get_vep_info(params)
            annotations = self._import_gnomad(vep_info)
            params.update({
                'annotations': annotations
            })
            with transaction.atomic():
                variant = self._import_variant(vep_info, params)
                transcripts = self._import_transcripts(variant, vep_info, params)
                if transcripts:
                    for _transcript in Field(data.get('SNV_info')).group_dict(config.get('snv_info')):
                        # Let's find the transcript result from VEP
                        vep_transcript = next(filter(lambda t: t.ensembl_id == _transcript.get('ensembl_id').split('.')[0], transcripts), None)
                        if vep_transcript:
                            log.info(f"Found vep transcript {vep_transcript.ensembl_id}")
                            # Prepare some values
                            # annotations = vep_transcript.copy()
                            # annotations.update(_transcript)
                            vep_transcript.annotations.update(_transcript)
                        else:
                            log.warning(f"VEP does not know {_transcript.get('ensembl_id')}")
                self._import_sample(params, variant)
                self._import_pubmed_evidences(vep_info, variant)
                self._import_disgenet(variant)
                 
        return variant
