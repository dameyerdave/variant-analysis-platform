from rest_framework import filters
from config.config import Config

class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        config = Config().as_dict()
        fields_config = view.__class__.__name__.replace('ViewSet', '').lower()
        default = []
        if fields_config and fields_config in config and 'search_fields' in config[fields_config]:
          default = config[fields_config]['search_fields']

        return default