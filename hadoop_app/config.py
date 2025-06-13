# Hadoop Configuration
HADOOP_CONFIG = {
    'HDFS': {
        'host': 'localhost',
        'port': 50070,
        'user': 'hdfs',
        'timeout': 10000,
        'monitoring': {
            'health_check_interval': 300,  # seconds
            'max_retries': 3,
            'retry_delay': 5  # seconds
        }
    },
    'HIVE': {
        'host': 'localhost',
        'port': 10000,
        'user': 'hive',
        'database': 'default',
        'auth': 'NONE',
        'monitoring': {
            'query_timeout': 300,  # seconds
            'max_connections': 10
        }
    },
    'MAPREDUCE': {
        'jobtracker': 'localhost:8088',
        'historyserver': 'localhost:19888',
        'monitoring': {
            'job_status_interval': 60,  # seconds
            'log_fetch_interval': 300  # seconds
        }
    },
    'MONITORING': {
        'cluster_health_check': {
            'interval': 300,  # seconds
            'endpoints': {
                'namenode': 'http://localhost:50070/jmx',
                'resourcemanager': 'http://localhost:8088/jmx',
                'historyserver': 'http://localhost:19888/jmx'
            }
        },
        'metrics_collection': {
            'enabled': True,
            'interval': 60,  # seconds
            'metrics': [
                'hdfs_capacity',
                'hdfs_used',
                'mapreduce_jobs',
                'yarn_containers',
                'hive_queries'
            ]
        }
    }
}

# Job Configuration Defaults
JOB_CONFIG_DEFAULTS = {
    'MAPREDUCE': {
        'queue': 'default',
        'memory': '1024',
        'vcores': '1',
        'monitoring': {
            'progress_interval': 10,  # seconds
            'log_level': 'INFO'
        }
    },
    'SPARK': {
        'master': 'yarn',
        'deploy_mode': 'cluster',
        'executor_memory': '2g',
        'executor_cores': '1',
        'monitoring': {
            'event_log_enabled': True,
            'event_log_dir': '/user/spark/applicationHistory'
        }
    },
    'PIG': {
        'pig_properties': {
            'pig.exec.mapPartAgg': 'true',
            'pig.exec.mapJoin.localThreshold': '100'
        },
        'monitoring': {
            'progress_interval': 15,  # seconds
            'log_retention': 7  # days
        }
    },
    'HIVE': {
        'hive_properties': {
            'hive.exec.reducers.bytes.per.reducer': '1073741824',
            'hive.exec.dynamic.partition.mode': 'nonstrict'
        },
        'monitoring': {
            'query_timeout': 300,  # seconds
            'result_cache_size': 10000000  # bytes
        }
    }
}
