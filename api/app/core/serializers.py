from rest_framework import serializers
from core.lookup import lookup


class VariantSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        _mutable = data._mutable
        data._mutable = True
        data['assembly'] = lookup.assembly.normalize(data['assembly'])
        data._mutable = _mutable
        return super().to_internal_value(data)
