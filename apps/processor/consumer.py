import asyncio
from confluent_kafka import Consumer, KafkaException
from .models import ClientDataRecord
from django.contrib.auth.models import User as Client
import os
from datetime import datetime
import pandas as pd
import json
import hashlib
import pyarrow as pa
import pyarrow.parquet as pq


consumer_config = {
  'bootstrap.servers': os.environ.get('KAFKA_BROKER_URL', 'localhost:9092'),
  'group.id': 'my-consumer-group',
  'auto.offset.reset': 'earliest',
  'enable.auto.commit': False
}

consumer = Consumer(consumer_config)

BATCH_SIZE = 10 # for testing purposes


def hash_record(record, client_id, datasource):
  unique_key = json.dumps({
    'client_id': client_id,
    'datasource': datasource,
    'date': record['date'],
    'campaign_id': record['campaign_id'],
    'ad_id': record['ad_id']
  }, sort_keys=True)
  return hashlib.sha256(unique_key.encode()).hexdigest()

async def process_batch(batch, client_id, datasource):
  if not batch:
    return

  client = Client.objects.get(client__id=client_id)
  records = {}
  hashes = set()

  for record in batch:
    record_hash = hash_record(record, client_id, datasource)
    records[record_hash] = record
    hashes.add(record_hash)
  
  existing_records = ClientDataRecord.objects.filter(client=client, record_hash__in=hashes)
  existing_hashes = set(existing_records.values_list('record_hash', flat=True))

  new_records = {h: v for h, v in records.items() if h not in existing_hashes}
  updated_records = {h: v for h, v in records.items() if h in existing_hashes}

  if new_records:
    current_hour = datetime.now().strftime('%H')
    storage_path = f's3://datalake/{client_id}/{datasource}/{datetime.now():%Y/%m/%d}/data_{current_hour}.parquet'
    df = pd.DataFrame(v for h, v in new_records.items())
    table = pa.Table.from_pandas(df)

    with s3.open(storage_path, 'wb') as f:
      pq.write_table(table, f)
    
    ClientDataRecord.objects.bulk_create([
      ClientDataRecord(
        client=client,
        record_hash=h,
        storage_paths=[storage_path],
        files=new_records[h].keys()
      ) for h in new_records
    ])
  for record in existing_records:
    table = pq.read_table([record.storage_path], filesystem=s3)
    new_fields = set(updated_records[record.record_hash].keys())
    old_fields = set(record.fields)
    diff_fields = new_fields - old_fields

    for f in diff_fields:
      col = pa.array([None]*len(table), type=pa.int64())
      table = table.append(f, col)
    pq.write_table(table, record.storage_path, filesystem=s3) # for backfill, we need to update the schema and pass the new schema
    meta_record = ClientDataRecord.objects.filter(client=client, record_hash=record.record_hash)
    meta_record.files = old_fields.union(diff_fields)
    meta_record.save()

async def consume():
  consumers = ClientDatasource.objects.filter(is_active=True)
  for consumer in consumers:
    client_id = consumer.client.id
    datasource = consumer.datasource.name
    topic_name = f'{client_id}.{datasource}'
    consumer.subscribe([topic_name]) # we need to read all the topics from the db and consume it

    try:
      batch = []
      BATCH_SIZE = 10 # for testing purposes

      while True:
        msg = await asyncio.to_thread(consumer.poll, timeout=1.0) # polling is blocking, so wrap it in executor
        if msg is None:
          if batch:
            await process_batch(batch, client_id, datasource)
            consumer.commit()
            batch = []
          await asyncio.sleep()
          continue

        if msg.error():
          continue
        
        batch.append(msg)

        if len(batch) >= BATCH_SIZE:
          await process_batch(batch, client_id, datasource)
          consumer.commit()
          batch = []
    except (KeyboardInterrupt, KafkaException) as e:
      print(f'Consumer error: {str(e)}')
    finally:
      consumer.close()

if __name__ == '__main__':
  asyncio.run(consume())