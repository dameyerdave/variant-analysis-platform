from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register
from drf_auto_endpoint.factories import serializer_factory
from core.helpers import q_from_config
from core.models import (Variant, Gene, Transcript, VariantConsequence, Evidence, TranscriptEvidence, Patient, Sample, SampleVariant, Phenotype)
from core.serializers import ExpandVariantSerializer, ExpandSampleVariantSerializer, ExpandTranscriptSerializer
from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from config.config import Config, ConfigFileNotFoundException
from core.helpers import q_or_list, q_from_config
from core.views import DefaultViewSet
from django.contrib.postgres.aggregates import ArrayAgg


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
    def queryset_extra(qs, _filter):
        # We add the transcript names to the queryset as well as the gene names
        config = Config()
        transcript_filter = q_from_config(config.get_filter('transcript', _filter), prefix='transcripts__')
        return qs.annotate(
                transcript_names=ArrayAgg('transcripts__name', filter=transcript_filter)
            ).annotate(
                gene_names=ArrayAgg('transcripts__gene__symbol', filter=transcript_filter, distinct=True)
            )

    model = Variant
    base_viewset = DefaultViewSet.build(model=model, expand_serializer=ExpandVariantSerializer, prefetch=[
        {'property': 'transcripts', 'model': Transcript}
    ], queryset_extra=queryset_extra)
    filter_fields = ['transcripts__id', 'transcripts__name']
    extra_fields = ['transcript_names', 'gene_names']

@register
class GeneEndpoint(DefaultEndpoint):
    model = Gene
    filter_fields = ['symbol', 'transcripts__id', 'transcripts__name']
    extra_fields = []

    base_viewset = DefaultViewSet.build(model=model)


@register
class TranscriptEndpoint(DefaultEndpoint):
    model = Transcript
    base_viewset = DefaultViewSet.build(model=model, expand_serializer=ExpandTranscriptSerializer, related=['gene'])
    filter_fields = ['gene__symbol', 'variant__id']


@register
class VariantConsequenceEndpoint(DefaultEndpoint):
    model = VariantConsequence
    filter_fields = ['term']

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
    base_viewset = DefaultViewSet.build(model=model, expand_serializer=ExpandSampleVariantSerializer, prefetch=[
        { 'property': 'sample', 'model': Sample }, 
        { 'property': 'variant', 'model': Variant, 'prefetch': { 'property': 'transcripts', 'model': Transcript }}
    ])
    filter_fields = ['sample__id', 'variant__transcripts__gene__symbol']

    

@register
class PhenotypeEndpoint(DefaultEndpoint):
    model = Phenotype

class SearchViewSet(ObjectMultipleModelAPIViewSet):
    def get_querylist(self):
        try:
            config = Config().current
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
        
    