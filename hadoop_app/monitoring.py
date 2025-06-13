import requests
import json
from datetime import datetime
from .config import HADOOP_CONFIG
import logging

logger = logging.getLogger(__name__)

class HadoopMonitor:
    def __init__(self):
        self.config = HADOOP_CONFIG
        self.metrics = {}
        
    def check_cluster_health(self):
        """Check overall Hadoop cluster health"""
        health = {}
        
        for service, endpoint in self.config['MONITORING']['cluster_health_check']['endpoints'].items():
            try:
                response = requests.get(endpoint)
                if response.status_code == 200:
                    health[service] = {
                        'status': 'HEALTHY',
                        'timestamp': datetime.now().isoformat(),
                        'metrics': response.json()
                    }
                else:
                    health[service] = {
                        'status': 'UNHEALTHY',
                        'timestamp': datetime.now().isoformat(),
                        'error': f"HTTP {response.status_code}"
                    }
            except Exception as e:
                health[service] = {
                    'status': 'UNHEALTHY',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
                logger.error(f"Failed to check {service} health: {e}")
        
        return health

    def collect_metrics(self):
        """Collect Hadoop cluster metrics"""
        metrics = {}
        
        if not self.config['MONITORING']['metrics_collection']['enabled']:
            return metrics
            
        for metric in self.config['MONITORING']['metrics_collection']['metrics']:
            try:
                if metric == 'hdfs_capacity':
                    metrics['hdfs_capacity'] = self._get_hdfs_capacity()
                elif metric == 'hdfs_used':
                    metrics['hdfs_used'] = self._get_hdfs_used()
                elif metric == 'mapreduce_jobs':
                    metrics['mapreduce_jobs'] = self._get_mapreduce_jobs()
                elif metric == 'yarn_containers':
                    metrics['yarn_containers'] = self._get_yarn_containers()
                elif metric == 'hive_queries':
                    metrics['hive_queries'] = self._get_hive_queries()
            except Exception as e:
                logger.error(f"Failed to collect {metric} metrics: {e}")
                metrics[metric] = {'error': str(e)}
        
        return metrics

    def _get_hdfs_capacity(self):
        """Get HDFS capacity metrics"""
        endpoint = self.config['MONITORING']['cluster_health_check']['endpoints']['namenode']
        response = requests.get(endpoint)
        data = response.json()
        
        for bean in data['beans']:
            if bean['name'] == 'Hadoop:service=NameNode,name=FSNamesystemState':
                return {
                    'total': bean['CapacityTotal'],
                    'used': bean['CapacityUsed'],
                    'remaining': bean['CapacityRemaining'],
                    'timestamp': datetime.now().isoformat()
                }
        
        return {'error': 'HDFS capacity metrics not found'}

    def _get_hdfs_used(self):
        """Get HDFS usage metrics"""
        endpoint = self.config['MONITORING']['cluster_health_check']['endpoints']['namenode']
        response = requests.get(endpoint)
        data = response.json()
        
        for bean in data['beans']:
            if bean['name'] == 'Hadoop:service=NameNode,name=FSNamesystemState':
                return {
                    'used': bean['CapacityUsed'],
                    'used_percent': bean['PercentUsed'],
                    'timestamp': datetime.now().isoformat()
                }
        
        return {'error': 'HDFS usage metrics not found'}

    def _get_mapreduce_jobs(self):
        """Get MapReduce job metrics"""
        endpoint = self.config['MONITORING']['cluster_health_check']['endpoints']['historyserver']
        response = requests.get(endpoint)
        data = response.json()
        
        for bean in data['beans']:
            if bean['name'] == 'Hadoop:service=HistoryServer,name=JobHistoryStatistics':
                return {
                    'total_jobs': bean['TotalJobs'],
                    'failed_jobs': bean['FailedJobs'],
                    'successful_jobs': bean['SuccessfulJobs'],
                    'timestamp': datetime.now().isoformat()
                }
        
        return {'error': 'MapReduce job metrics not found'}

    def _get_yarn_containers(self):
        """Get YARN container metrics"""
        endpoint = self.config['MONITORING']['cluster_health_check']['endpoints']['resourcemanager']
        response = requests.get(endpoint)
        data = response.json()
        
        for bean in data['beans']:
            if bean['name'] == 'Hadoop:service=ResourceManager,name=RMNMInfo':
                return {
                    'total_containers': bean['TotalContainers'],
                    'active_containers': bean['ActiveContainers'],
                    'timestamp': datetime.now().isoformat()
                }
        
        return {'error': 'YARN container metrics not found'}

    def _get_hive_queries(self):
        """Get Hive query metrics"""
        endpoint = self.config['HIVE']['host']
        try:
            # This would typically connect to Hive's JMX endpoint
            # For now, we'll return a placeholder
            return {
                'active_queries': 0,
                'completed_queries': 0,
                'failed_queries': 0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

# Singleton instance of the monitor
hadoop_monitor = HadoopMonitor()
