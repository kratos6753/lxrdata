from django.db import models
from apps.commons.models import BaseModel, AuditModel
from fetcher.models import DataSource
from django.conf import settings


class ClientDatasource(BaseModel):
  client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  datasource = models.ForeignKey(DataSource)
  credentials = models.JSONField() # JSON field of {apikey: xxxx, apisecret: xxxx}
  is_active = models.BooleanField(default=True)


class ClientDataRecord(BaseModel, AuditModel):
  client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  record_hash = models.CharField(max_length=64, primary_key=True)
  storage_path = models.CharField(max_length=1024)
  files = models.JSONField() # list of fields/metrics currently stored for record, helped when linking duplicates