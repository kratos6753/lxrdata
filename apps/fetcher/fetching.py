import asyncio
import aiohttp
from .models import ClientDataSourceConfig

async def fetch_external_data(session, api_base_url, fields, client_name, source_name):
  params = {"fields": ",".join(fields)}
  try:
    async with session.get(f"{api_base_url}/mock_data", params=params) as response:
      if response.status == 200:
        data = await response.json()
        print(f'Fetched for {client_name} ({source_name}): {data}')
        return data
      else:
        print(f'Error fetching for {client_name}: {response.status}')
  except Exception as e:
    print(f'Exception for {client_name}: {str(e)}')

async def fetch_all_clients_data():
  configs = ClientDataSourceConfig.objects.filter(active=True)

  async with aiohttp.ClientSession() as session:
    tasks = []
    for config in configs:
      task = fetch_external_data(
        session,
        api_base_url=config.external_source.api_base_url,
        fields=config.fetch_config,
        client_name=config.client.name,
        source_name=config.external_source.name
      )
      tasks.append(task)
    results = await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
  asyncio.run(fetch_all_clients_data())