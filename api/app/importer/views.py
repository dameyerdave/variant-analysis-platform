from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from api.app.core.models import AlleleRegistry
from .proxys import vep, genenames, alleleregistry
from django.utils.translation import gettext as _
from core.models import Variant, Transcript, Gene, VariantConsequence
from django.db import transaction
from bioinfo_toolset.modules.formatter import transcript_name


class AddVepVariantView(APIView):
    def get(self, request, region):
        assembly = request.GET.get('assembly')
        canonical = request.GET.get('canonical') == 'true'
        GRCh37 = False
        if assembly:
            if assembly in ['GRCh37', 'hg19', 'old']:
                GRCh37 = True
        parts = region.split('_')
        if len(parts) < 3:
            return Response({'detail': _('region %(region)s is not in the required format') % {'region': region}},
                            status.HTTP_406_NOT_ACCEPTABLE)
        if len(parts) == 3:
            vep_resp = vep(f"{parts[0]}:{parts[1]}/{parts[2]}",
                       input_type='region', GRCh37=GRCh37, refseq=False)
        elif len(parts) == 4:
            vep_resp = vep(f"{parts[0]}:{parts[1]}_{parts[2]}/{parts[3]}",
                       input_type='region', GRCh37=GRCh37, refseq=False)
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
                        'most_severe_consequence': VariantConsequence.objects.get(term=vep_info.get('most_severe_consequence'))
                    }
                )
                for transcript_consequence in vep_info.get('transcript_consequences'):
                    if not canonical or transcript_consequence.get('canonical'):
                        gene, created = Gene.objects.get_or_create(
                            symbol=transcript_consequence.get('gene_symbol'),
                            ensembl_id=transcript_consequence.get('gene_id'),
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
            return Response(vep_info, status.HTTP_201_CREATED)
        else:
            return Response(vep_resp.json(), status.HTTP_400_BAD_REQUEST)
