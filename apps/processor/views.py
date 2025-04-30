from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
import os
import pyarrow.parquet as pq
from s3fs import S3FileSystem
from .models import ClientDataRecord


s3 = S3FileSystem(
  key=os.environ.get('AWS_ACCESS_KEY_ID'),
  secret=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

@api_view(['GET'])
def get_client_data(request):
  records = ClientDataRecord.objects.filter(client=request.client)
  paths = set(records.values_list('storage_path', flat=True))
  dataset = pq.ParquetDataset(paths, filesystem=s3, use_legacy_dataset=False)
  table = dataset.read()
  df = table.to_pandas()
  return JsonResponse(df.to_dict('records'), safe=False)
