import aiohttp
import asyncio
from celery import shared_task
from aiobreaker import CircuitBreaker
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from .producer import add_to_batch, flush_batch
import logging

logger = logging.getLogger(__name__)

# Per source breakers
breakers = {}

def get_breaker(source_name):
  if source_name not in breakers:
    breakers[source_name] = CircuitBreaker(fail_max=3, reset_timeout=30)
  return breakers[source_name]

@shared_task
def fetch_external_data_task(api_end_point, fields, client_name, source_name, headers):
  asyncio.run(_safe_fetch(api_end_point, fields, client_name, source_name, headers))
  flush_batch()

async def _safe_fetch(api_end_point, fields, client_name, source_name, headers):
  breaker = get_breaker(source_name)
  params = {"fields": ",".join(fields)}
  async with aiohttp.ClientSession(headers=headers) as session:
    try:
      result = await breaker.call(_fetch_with_retry, session, api_end_point, params)
      add_to_batch(client_name, source_name, result)
      print(f'Fetched data for {client_name} ({source_name}): {result}')
      return result
    except Exception as e:
      print(f'Fetch failed for {client_name} ({source_name}): {str(e)}')

@shared_task
def fetch_all_clients_data():
  from .models import ScheduleJob

  jobs = ScheduleJob.objects.filter(is_active=True)
  for job in jobs:
    fetch_external_data_task.delay(
      api_end_point=job.datasource.api_end_point,
      fields=job.fetch_fields,
      client_name=job.client.username,
      source_name=job.datasource.name,
      headers=job.auth_credentials
    )

@retry(
  wait=wait_fixed(2),
  stop=stop_after_attempt(3),
  retry=retry_if_exception_type(aiohttp.ClientError)
)
async def _fetch_with_retry(session, url, params):
  async with session.get(url, params=params) as response:
    if response.status != 200:
      raise Exception(f'Fetch failed, status={response.status}')
    return await response.json()
