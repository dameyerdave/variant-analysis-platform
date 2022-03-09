from rest_framework.metadata import SimpleMetadata
from rest_framework.schemas.openapi import AutoSchema


class APIMetadata(SimpleMetadata):
    """
    Extended metadata generator.

    To use this we need to adjust the settings accordingly:
    REST_FRAMEWORK = {
        'DEFAULT_METADATA_CLASS': 'meta.serializers.APIMetadata',
    }
    """

    def get_field_info(self, field):
        field_info = super().get_field_info(field)

        # Add extra validators using the OpenAPI schema generator
        validators = {}
        AutoSchema()._map_field_validators(field, validators)
        extra_validators = ['format', 'pattern']
        for validator in extra_validators:
            if validators.get(validator, None):
                field_info[validator] = validators[validator]

        # Add additional data from serializer
        field_info['initial'] = field.initial
        field_info['field'] = field.field_name
        field_info['write_only'] = field.write_only
        if hasattr(field, 'choices') and field.choices:
            field_info['choices'] = [
                {
                    'label': label,
                    'value': value
                }
                for value, label in field.choices.items()
            ]

        return field_info
