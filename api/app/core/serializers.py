from rest_framework import serializers
from core.lookup import lookup
from core.models import (Variant, Sample, Transcript, SampleVariant, Gene, Evidence, VariantEvidence)
from django.contrib.auth import get_user_model

from users.managers import CustomUserManager

class DefaultModelSerializer(serializers.ModelSerializer):
    """ The default model serializer that supports additional functionality """
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request: 
            _only = self.context.get('request').query_params.get('only')
            _defer = self.context.get('request').query_params.get('defer')
            if _only:
                _only = _only.split(',')
                fields = {k: v for k, v in fields.items() if k in _only}
            if _defer:
                _defer = _defer.split(',')
                fields = {k: v for k, v in fields.items() if k not in _defer}
        return fields

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'

class GeneSerializer(DefaultModelSerializer):
    class Meta:
        model = Gene
        fields = '__all__'

class TranscriptSerializer(DefaultModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'

class VariantSerializer(DefaultModelSerializer):
    def to_internal_value(self, data):
        # To support different names for the same assembly
        # _mutable = data._mutable
        # data._mutable = True
        if 'assembly' in data:
            data['assembly'] = lookup.assembly.normalize(data['assembly'])
        # data._mutable = _mutable
        return super().to_internal_value(data)

    class Meta:
        model = Variant
        fields = '__all__'
        
class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = '__all__'

###
# Expanded readonly serializers
###

class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        # print(self.__class__.__name__, 'get_fields', fields.keys())
        return fields

class ExpandTranscriptSerializer(ReadOnlyModelSerializer):
    extra = serializers.ReadOnlyField()
    gene = GeneSerializer()

    class Meta:
        model = Transcript
        fields = '__all__'

class ExpandVariantSerializer(ReadOnlyModelSerializer):
    extra = serializers.ReadOnlyField()
    gene_names = serializers.ReadOnlyField()
    transcripts = ExpandTranscriptSerializer(many=True)

    class Meta:
        model = Variant
        fields = '__all__'

class ExpandSampleVariantSerializer(ReadOnlyModelSerializer):
    sample = SampleSerializer()
    variant = ExpandVariantSerializer()

    class Meta:
        model = SampleVariant
        fields = '__all__'

class ExpandVariantEvidenceSerializer(ReadOnlyModelSerializer):
    evidence = EvidenceSerializer()

    class Meta:
        model = VariantEvidence
        fields = '__all__'