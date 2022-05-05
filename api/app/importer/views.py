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


class AddVepVariantView(APIView):
    def get(self, request, region):
        import_config = None
        import_strategy = VepStrategy()
        assembly = request.GET.get('assembly')
        canonical = request.GET.get('canonical') == 'true'
        GRCh37 = False
        if assembly:
            if assembly in ['GRCh37', 'hg19', 'old']:
                GRCh37 = True
        parts = region.split('_')
        if len(parts) < 4:
            return Response({'detail': _('region %(region)s is not in the required format') % {'region': region}},
                            status.HTTP_406_NOT_ACCEPTABLE)
        # if len(parts) == 3:
        #     vep_resp = vep(f"{parts[0]}:{parts[1]}/{parts[2]}",
        #                input_type='region', GRCh37=GRCh37, refseq=False)
        # elif len(parts) == 4:
        #     vep_resp = vep(f"{parts[0]}:{parts[1]}_{parts[2]}/{parts[3]}",
        #                input_type='region', GRCh37=GRCh37, refseq=False)
        if len(parts) == 4:
            imported, response = import_strategy.import_one({
                'config': import_config,
                'chr': parts[0],
                'start': parts[1],
                'ref': parts[2],
                'alt': parts[3]
            })
        elif len(parts) == 5:
            imported, response = import_strategy.import_one({
                'config': import_config,
                'chr': parts[0],
                'start': parts[1],
                'ref': parts[2],
                'alt': parts[3]
            })
        else:
            imported, response = False, {}
        
        if imported:
            return Response(response, status.HTTP_201_CREATED)
        else:
            return Response(response, status.HTTP_400_BAD_REQUEST)
