from confluent_kafka import Producer
import json
import os
from collections import defaultdict

producer_config = {
  'bootstrap.servers': os.environ.get('KAFKA_BROKER_URL', 'localhost:9092')
}

producer = Producer(producer_config)

# in-memory buffer
batch_buffer = defaultdict(list)
BATCH_SIZE = 10 # for testing purposes, for production it will be 1000 or so depending on the TPS

def add_to_batch(client_name, source_name, payload):
  topic_name = f'{client_name}.{source_name}'
  batch_buffer[topic_name].append(payload)

  if len(batch_buffer[topic_name]) >= BATCH_SIZE:
    flush_batch(topic_name)

def flush_batch(topic_name=None):
  if topic_name:
    topics = [topic_name]
  else:
    topics = batch_buffer.keys()
  
  for topic in topics:
    messages = batch_buffer[topic]
    if not messages:
      continue
    try:
      payload = json.dumps(messages).encode('utf-8')
      producer.produce(topic=topic, value=payload)
      producer.flush()
      print(f'Flushed {len(messages)} messages to Kafka topic: {topic}')
      batch_buffer[topic] = []
    except Exception as e:
      print(f'Error batch sending to Kafka topic {topic}: {str(e)}')

def send_to_kafka(client_name, source_name, payload):
  topic_name = f'{client_name}.{source_name}'
  try:
    producer.produce(
      topic=topic_name,
      key=client_name,
      value=json.dumps(payload).encode('utf-8')
    )
    producer.flush()

    print(f'Sent data to Kafka topic: {topic_name}')
  except Exception as e:
    print(f'Error sending to kafka: {str(e)}')
    raise
