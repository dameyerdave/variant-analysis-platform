from rest_framework import serializers
from core.lookup import lookup
from core.models import Variant, Sample, Transcript, SampleVariant, Gene

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'

class GeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gene
        fields = '__all__'

class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        # To support different names for the same assembly
        _mutable = data._mutable
        data._mutable = True
        data['assembly'] = lookup.assembly.normalize(data['assembly'])
        data._mutable = _mutable
        return super().to_internal_value(data)

    class Meta:
        model = Variant
        fields = '__all__'
        

###
# Expanded readonly serializers
###

class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

class ExpandTranscriptSerializer(ReadOnlyModelSerializer):
    gene = GeneSerializer()

    class Meta:
        model = Transcript
        fields = '__all__'

class ExpandVariantSerializer(ReadOnlyModelSerializer):
    transcripts = ExpandTranscriptSerializer(many=True)
    transcript_names = serializers.ReadOnlyField()
    gene_names = serializers.ReadOnlyField()

    class Meta:
        model = Variant
        fields = '__all__'

class ExpandSampleVariantSerializer(ReadOnlyModelSerializer):
    sample = SampleSerializer()
    variant = ExpandVariantSerializer()

    class Meta:
        model = SampleVariant
        fields = '__all__'