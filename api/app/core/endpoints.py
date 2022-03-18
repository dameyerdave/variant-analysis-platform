from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register
from core.models import Variant, Gene, Transcript, VariantConsequence
from rest_framework import serializers, relations
from core.serializers import VariantSerializer


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


@register
class GeneEndpoint(DefaultEndpoint):
    model = Gene
    filter_fields = ['transcripts__name']
    search_fields = ['symbol']
    extra_fields = []


@register
class TranscriptEndpoint(DefaultEndpoint):
    model = Transcript
    filter_fields = ['gene']
    search_fields = ['name']


@register
class VariantConsequenceEndpoint(DefaultEndpoint):
    model = VariantConsequence
    filter_fields = ['term']
    search_fields = ['term', 'hr_term', 'accession']
