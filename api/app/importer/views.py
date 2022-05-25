from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from api.app.core.models import AlleleRegistry
from importer.proxys import vep, vep_offline, genenames, alleleregistry
# from bioinfo_toolset.modules.vep_offline import OfflineVep
from django.utils.translation import gettext as _
from core.models import Variant, Transcript, Gene, VariantConsequence
from django.db import transaction
from bioinfo_toolset.modules.formatter import transcript_name
from importer.strategies import VepStrategy
from core.serializers import ExpandVariantSerializer


class AddVepVariantView(APIView):
    def get(self, request, region):
        import_config = None
        import_strategy = VepStrategy()
        parts = region.split('_')
        if len(parts) < 4 or len(parts) > 5:
            return Response({'detail': _('region %(region)s is not in the required format') % {'region': region}},
                            status.HTTP_406_NOT_ACCEPTABLE)
        try:
            params = {
                    'config': import_config,
                    'vep_options': request.GET,
                    'chr': parts[0],
                    'start': parts[1],
                    'ref': parts[2],
                    'alt': parts[3],
                }
            if len(parts) == 5:
                params.update({
                    'end': parts[2],
                    'ref': parts[3],
                    'alt': parts[4],
                })
            variant = import_strategy.import_one(params)
            serialized = ExpandVariantSerializer(variant)
            return Response(serialized.data, status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({'detail': _('Error importing variant %(region)s: %(exception)s') % {'region': region, 'exception': ex}}, 
                status.HTTP_400_BAD_REQUEST)
