from rest_framework import serializers
from core.lookup import lookup
from core.models import Variant, Sample, Transcript, SampleVariant
from core.helpers import q_from_config
from config.config import Config


class FilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        # We filter nested serializers in representation
        filter = self.context['request'].query_params.get('filter')
        if not filter:
            # We set the default filter
            filter = 'default'
        config = Config().as_dict()
        model_name = data.model.__name__.lower()
        if model_name in config and 'filters' in config[model_name] and filter in config[model_name]['filters']:
            _filter = q_from_config(config[model_name]['filters'][filter])
            print('_filter', _filter)
            data = data.filter(_filter)
        return super().to_representation(data)

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        _mutable = data._mutable
        data._mutable = True
        data['assembly'] = lookup.assembly.normalize(data['assembly'])
        data._mutable = _mutable
        return super().to_internal_value(data)

    class Meta:
        model = Variant
        fields = '__all__'

class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        list_serializer_class = FilteredListSerializer
        fields = '__all__'

class ExpandedVariantSerializer(VariantSerializer):
    transcripts = TranscriptSerializer(many=True)

class ExpandedSampleVariantSerializer(serializers.ModelSerializer):
    sample = SampleSerializer()
    variant = ExpandedVariantSerializer()

    class Meta:
        model = SampleVariant
        fields = '__all__'
