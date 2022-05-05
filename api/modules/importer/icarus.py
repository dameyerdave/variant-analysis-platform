from importer.strategies import BaseStrategy
from importer.helpers import Field
from core.models import Sample, SampleVariant, Variant, Gene, Transcript, VariantTranscript
from django.db import transaction
from importer.proxys import genenames
from bioinfo_toolset.modules.formatter import transcript_name


class ImportStrategy(BaseStrategy):
    def import_one(self, params):
        config = params.get('config')
        data = params.get('data')
        if data:
            with transaction.atomic():
                variant, _ = Variant.objects.update_or_create(
                    assembly='GRCh38',
                    chromosome=params.get('chr'),
                    start=params.get('start'),
                    end=params.get('start'),
                    allele_string=f"{params.get('ref')}/{params.get('alt')}",
                    strand=None,
                    variant_type=data.get('Variant_type'),
                    defaults={
                        'most_severe_consequence': None,
                        'annotations': None
                    }
                )
                for _transcript in Field(data.get('SNV_info')).group_dict(config.get('snv_info')):
                    gene, created = Gene.objects.update_or_create(
                        symbol=_transcript.get('gene')
                    )
                    if created:
                        genenames_resp = genenames(
                            _transcript.get('gene'))
                        if genenames_resp.ok:
                            gene_info = genenames_resp.json()
                            if len(gene_info['response']['docs']) > 0:
                                gene.annotations = gene_info['response']['docs'][0]
                                gene.save()
                    _transcript_name, found = transcript_name({'hgvsp': f"_:{_transcript.get('protein_change')}"})
                    if _transcript_name == '.':
                        _transcript_name = _transcript.get('dna_change')
                        if _transcript_name == '.':
                            _transcript_name = f"{params.get('chr')}:{params.get('start')}{params.get('ref')}>{params.get('alt')}"
                    transcript, created = Transcript.objects.update_or_create(
                        ensembl_id=_transcript.get('ensembl_id').split('.')[0],
                        defaults={
                            'name': _transcript_name,
                            'hgvsc': ':'.join((_transcript.get('ensembl_id'), _transcript.get('dna_change'))),
                            'hgvsp': ':'.join((_transcript.get('ensembl_id'), _transcript.get('protein_change')),
                            'gene': gene,
                            'annotations': _transcript
                        }
                    )
                    variantTranscript = VariantTranscript.objects.update_or_create(
                        variant = variant
                        transcript = transcript
                        defaults = {
                            'rank': max(int(_transcript.get('rank').split('&')[0]), 0),
                        }
                    )
                    if created:
                        print(f"transcript added {transcript}")
                if params.get('sample_id'):
                    sample, _ = Sample.objects.get_or_create(id=params.get('sample_id'))
                    sampleVariant, _ = SampleVariant.objects.get_or_create(
                        sample=sample,
                        variant=variant,
                        zygosity=data.get('Zygosity').split(':')[0]
                    )    
        return True, data
