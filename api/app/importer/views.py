from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .proxys import vep, genenames
from django.utils.translation import gettext as _
from core.models import Variant, Transcript, Gene, VariantConsequence
from django.db import transaction
from bioinfo_toolset.modules.formatter import transcript_name


class AddVepVariantView(APIView):
    def get(self, request, region):
        assembly = request.GET.get('assembly')
        GRCh37 = False
        if assembly:
            if assembly in ['GRCh37', 'hg19', 'old']:
                GRCh37 = True
        parts = region.split('_')
        if len(parts) < 3:
            return Response({'detail': _('region %(region)s is not in the required format') % {'region': region}},
                            status.HTTP_406_NOT_ACCEPTABLE)
        vep_resp = vep(f"{parts[0]}:{parts[1]}/{parts[2]}",
                       input_type='region', GRCh37=GRCh37, refseq=False)
        if vep_resp.ok:
            vep_info = vep_resp.json()[0]
            with transaction.atomic():
                variant, _ = Variant.objects.get_or_create(
                    assembly=vep_info.get('assembly_name'),
                    chromosome=vep_info.get('seq_region_name'),
                    start=vep_info.get('start'),
                    end=vep_info.get('end'),
                    allele_string=vep_info.get('allele_string'),
                    strand=vep_info.get('strand'),
                    most_severe_consequence=VariantConsequence.objects.get(
                        term=vep_info.get('most_severe_consequence')),
                    variant_type='SNV'
                )
                for transcript_consequence in vep_info.get('transcript_consequences'):
                    if transcript_consequence.get('canonical'):
                        gene, created = Gene.objects.get_or_create(
                            symbol=transcript_consequence.get('gene_symbol'),
                            ensembl_id=transcript_consequence.get('gene_id'),
                            annotations={}
                        )
                        if created:
                            genenames_resp = genenames(
                                transcript_consequence.get('gene_symbol'))
                            if genenames_resp.ok:
                                gene_info = genenames_resp.json()
                                gene.annotations = gene_info['response']['docs'][0]
                                gene.save()
                        _transcript_name, found = transcript_name(
                            transcript_consequence)
                        if found:
                            Transcript.objects.get_or_create(
                                name=_transcript_name,
                                ensembl_id=transcript_consequence.get(
                                    'transcript_id'),
                                hgvsc=transcript_consequence.get(
                                    'hgvsc'),
                                hgvsp=transcript_consequence.get('hgvsp'),
                                gene=gene,
                                variant=variant,
                                annotations=transcript_consequence
                            )
            return Response(vep_info, status.HTTP_201_CREATED)
        else:
            return Response(vep_resp.json(), status.HTTP_400_BAD_REQUEST)
