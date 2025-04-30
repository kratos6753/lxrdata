from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

schedule, created = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)

PeriodicTask.objects.create(
  interval=schedule,
  name='Fetch All Clients Data',
  task='fetcher.fetching.fetch_all_clients_data',
  args=json.dumps([])
)
