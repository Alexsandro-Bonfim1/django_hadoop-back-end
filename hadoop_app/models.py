from django.db import models
from django.contrib.auth.models import User

class HDFSFile(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=500)
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class HiveQuery(models.Model):
    query = models.TextField()
    result = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='PENDING')

class HadoopJob(models.Model):
    JOB_TYPES = (
        ('MAPREDUCE', 'MapReduce'),
        ('SPARK', 'Spark'),
        ('PIG', 'Pig'),
        ('HIVE', 'Hive'),
    )
    
    name = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES)
    configuration = models.JSONField()
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class HadoopMetric(models.Model):
    METRIC_TYPES = [
        ('HDFS_CAPACITY', 'HDFS Capacity'),
        ('HDFS_USAGE', 'HDFS Usage'),
        ('MAPREDUCE_JOBS', 'MapReduce Jobs'),
        ('YARN_CONTAINERS', 'YARN Containers'),
        ('HIVE_QUERIES', 'Hive Queries')
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    cluster_name = models.CharField(max_length=255, default='default')
    
    class Meta:
        ordering = ['-timestamp']
