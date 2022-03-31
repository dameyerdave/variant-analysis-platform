from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register, router
from drf_auto_endpoint.factories import serializer_factory
from core.models import Variant, Gene, Transcript, VariantConsequence
from rest_framework import serializers, relations
from core.serializers import VariantSerializer
from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from django.db.models import Q

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

class SearchViewSet(ObjectMultipleModelAPIViewSet):
    def get_querylist(self):
        query = self.request.GET.get('q')    
        if query:
            querylist = [
                {
                    'queryset': Variant.objects.filter(
                        Q(most_severe_consequence__term__icontains=query)
                    ), 
                    'serializer_class': serializer_factory(VariantEndpoint, fields='__all__'), 
                    'label': 'variants'
                },
                {
                    'queryset': Transcript.objects.filter(
                        Q(gene__symbol__icontains=query) | 
                        Q(name__icontains=query) |
                        Q(ensembl_id__icontains=query) |
                        Q(hgvsc__icontains=query) |
                        Q(hgvsp__icontains=query)
                    ), 
                    'serializer_class': serializer_factory(TranscriptEndpoint, fields='__all__'), 
                    'label': 'transcripts'
                },
                {
                    'queryset': Gene.objects.filter(Q(symbol__icontains=query) | Q(ensembl_id__icontains=query)), 
                    'serializer_class': serializer_factory(GeneEndpoint, fields='__all__'), 
                    'label': 'genes'
                },
            ]
            return querylist
        return []
    