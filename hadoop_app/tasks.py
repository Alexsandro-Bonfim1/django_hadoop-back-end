from celery import shared_task
from .models import HadoopMetric
from .monitoring import hadoop_monitor
import json
from datetime import datetime

@shared_task
def collect_metrics():
    """Periodic task to collect and store Hadoop metrics"""
    try:
        metrics = hadoop_monitor.collect_metrics()
        
        for metric_type, value in metrics.items():
            HadoopMetric.objects.create(
                metric_type=metric_type.upper(),
                value=value,
                cluster_name='default'
            )
            
        return f"Successfully collected metrics at {datetime.now()}"
    except Exception as e:
        return f"Error collecting metrics: {str(e)}"

@shared_task
def check_cluster_health():
    """Periodic task to check cluster health"""
    try:
        health = hadoop_monitor.check_cluster_health()
        
        # Store health metrics
        HadoopMetric.objects.create(
            metric_type='CLUSTER_HEALTH',
            value=health,
            cluster_name='default'
        )
        
        return f"Successfully checked cluster health at {datetime.now()}"
    except Exception as e:
        return f"Error checking cluster health: {str(e)}"
