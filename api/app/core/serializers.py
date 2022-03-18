from rest_framework import serializers
from core.lookup import lookup


class VariantSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        data['assembly'] = lookup.assembly.normalize(data['assembly'])
        return super().to_internal_value(data)
