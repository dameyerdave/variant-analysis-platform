from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register, router
from drf_auto_endpoint.factories import serializer_factory
from simplejson import load
from core.models import (Variant, Gene, Transcript, VariantConsequence, Evidence, TranscriptEvidence, Patient, Sample, SampleVariant)
from rest_framework.response import Response
from rest_framework import status
from core.serializers import VariantSerializer
from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from django.db.models import Q
from config.config import Config, ConfigFileNotFoundException
from core.helpers import q_or_list



class DefaultEndpoint(Endpoint):
    include_str = False
    extra_fields = ['extra']

    def get_url(self):
        """ The core endpoint defaults to not include the application name in the apis url. """
        if hasattr(self, 'url') and self.url is not None:
            return self.url

        return '{}'.format(self.model_name.replace('_', '-'))


@register
class VariantEndpoint(DefaultEndpoint):
    model = Variant
    base_serializer = VariantSerializer
    filter_fields = ['transcripts__id', 'transcripts__name']
    search_fields = ['transcripts__name']

@register
class GeneEndpoint(DefaultEndpoint):
    model = Gene
    filter_fields = ['symbol', 'transcripts__id', 'transcripts__name']
    search_fields = ['symbol']
    extra_fields = []


@register
class TranscriptEndpoint(DefaultEndpoint):
    model = Transcript
    filter_fields = ['gene', 'variant__id']
    search_fields = ['name']


@register
class VariantConsequenceEndpoint(DefaultEndpoint):
    model = VariantConsequence
    filter_fields = ['term']
    search_fields = ['term', 'hr_term', 'accession']

@register
class EvidenceEndpoint(DefaultEndpoint):
    model = Evidence

@register
class TranscriptEvidenceEndpoint(DefaultEndpoint):
    model = TranscriptEvidence

@register
class PatientEndpoint(DefaultEndpoint):
    model = Patient

@register
class SampleEndpoint(DefaultEndpoint):
    model = Sample

@register
class SampleVariantEndpoint(DefaultEndpoint):
    model = SampleVariant

class SearchViewSet(ObjectMultipleModelAPIViewSet):
    def get_querylist(self):
        try:
            config = Config().config
            query = self.request.GET.get('q')    
            if query:
                # Generate the predicates from the config
                variant_predicates = q_or_list(config.variant.search_fields, query, op='icontains')
                transcript_predicates = q_or_list(config.transcript.search_fields, query, op='icontains')
                gene_predicates = q_or_list(config.gene.search_fields, query, op='icontains')
                querylist = [
                    {
                        'queryset': Variant.objects.filter(
                            variant_predicates
                        ), 
                        'serializer_class': serializer_factory(VariantEndpoint, fields='__all__'), 
                        'label': 'variants'
                    },
                    {
                        'queryset': Transcript.objects.filter(
                            transcript_predicates
                        ), 
                        'serializer_class': serializer_factory(TranscriptEndpoint, fields='__all__'), 
                        'label': 'transcripts'
                    },
                    {
                        'queryset': Gene.objects.filter(
                            gene_predicates
                        ), 
                        'serializer_class': serializer_factory(GeneEndpoint, fields='__all__'), 
                        'label': 'genes'
                    },
                ]
                return querylist
            return []
        except ConfigFileNotFoundException as ex:
            return []
        
    