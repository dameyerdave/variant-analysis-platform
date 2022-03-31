from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings

import yaml
from yaml.loader import SafeLoader
from os.path import join, isfile

class ConfigView(APIView):
    def get(self, request, use_config='default'):
        """ Returns the content of the config file, default is the default.yml """
        config_file = join(settings.CONFIG_DIR, f"{use_config}.yml")
        if not isfile(config_file):
            return Response({'detail': f"Config file {config_file} not found."}, status.HTTP_404_NOT_FOUND)

        with open(config_file, 'r') as cf:
            config = yaml.load(cf, Loader=SafeLoader)

        return Response(config, status.HTTP_200_OK) 


