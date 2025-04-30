from rest_framework import serializers
from .models import ClientDataSourceConfig


class ClientDataSourceConfigSerializer(serializers.ModelSerializer):
  class Meta:
    model = ClientDataSourceConfig
    fields = '__all__'
