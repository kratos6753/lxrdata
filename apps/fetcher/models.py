from django.conf import settings
from django.db import models
from apps.commons.models import BaseModel, AuditModel


class DataSource(BaseModel, AuditModel):
  name = models.CharField(max_length=255)
  api_end_point = models.URLField()
  description = models.TextField(blank=True)
  auth_type = models.CharField(max_length=50, choices=(('api_key', 'API Key'), ('none', 'None')))

  class Meta:
    unique_together = ('name', 'api_base_url')


class ScheduleJob(BaseModel, AuditModel):

  SCHEDULE_DAILY = 'daily'
  SCHEDULE_HOURLY = 'hourly'
  SCHEDULE_EVERY_6_HOURS = 'every_6h'
  SCHEDULE_CHOICES = [
    (SCHEDULE_DAILY, 'Daily'),
    (SCHEDULE_HOURLY, 'Hourly'),
    (SCHEDULE_EVERY_6_HOURS, 'Every 6 Hours'),
  ]

  name = models.CharField(max_length=255)
  schedule_type = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default=SCHEDULE_DAILY)
  schedule_time = models.TimeField(null=True, blank=True, help_text='Start time for daily job (HH:MM)')
  is_active = models.BooleanField(default=True)
  client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE)
  task_id = models.CharField(max_length=255, blank=True, editable=False)
  auth_credentials = models.JSONField()
  fetch_fields = models.JSONField()
  
  class Meta:
    unique_together = ('client', 'datasource')
  
  def __str__(self):
    return f'{self.name} ({self.schedule_type})'
