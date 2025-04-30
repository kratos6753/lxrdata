from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from .models import ScheduleJob

@receiver(post_save, sender=ScheduleJob)
def manage_celery_task(sender, instance, created, **kwargs):
  if not created and instance.task_id:
    PeriodicTask.objects.filter(id=instance.tas)