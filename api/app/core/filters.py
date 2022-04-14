from django_filters import filters
from core.models import SampleVariant

class GeneSymbolFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = SampleVariant
        fields = ['variant']