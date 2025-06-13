from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from hadoop_app.tasks import collect_metrics, check_cluster_health

class Command(BaseCommand):
    help = 'Initialize monitoring system with periodic tasks'

    def handle(self, *args, **options):
        # Create interval schedules if they don't exist
        try:
            schedule_60s = IntervalSchedule.objects.get(every=60, period=IntervalSchedule.SECONDS)
        except IntervalSchedule.DoesNotExist:
            schedule_60s = IntervalSchedule.objects.create(
                every=60,
                period=IntervalSchedule.SECONDS
            )

        try:
            schedule_300s = IntervalSchedule.objects.get(every=300, period=IntervalSchedule.SECONDS)
        except IntervalSchedule.DoesNotExist:
            schedule_300s = IntervalSchedule.objects.create(
                every=300,
                period=IntervalSchedule.SECONDS
            )

        # Create periodic tasks
        try:
            PeriodicTask.objects.get(name='collect_metrics')
        except PeriodicTask.DoesNotExist:
            PeriodicTask.objects.create(
                name='collect_metrics',
                task='hadoop_app.tasks.collect_metrics',
                interval=schedule_60s,
                enabled=True
            )

        try:
            PeriodicTask.objects.get(name='check_cluster_health')
        except PeriodicTask.DoesNotExist:
            PeriodicTask.objects.create(
                name='check_cluster_health',
                task='hadoop_app.tasks.check_cluster_health',
                interval=schedule_300s,
                enabled=True
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized monitoring system'))
