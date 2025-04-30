from rest_framework import viewsets
from .models import ClientDataSourceConfig
from .serializers import ClientDataSourceConfigSerializer


class ClientDataSourceConfigViewSet(viewsets.ModelViewSet):
  queryset = ClientDataSourceConfig.objects.all()
  serializer_class = ClientDataSourceConfigSerializer
