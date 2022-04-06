from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from config.config import Config, ConfigFileNotFoundException

class ConfigView(APIView):
    def get(self, request):
        """ Returns the content of the config file, default is the default.yml """
        try:
            config = Config().as_dict()
        except ConfigFileNotFoundException as ex:
            return Response(ex, status.HTTP_404_NOT_FOUND)

        return Response(config, status.HTTP_200_OK) 


