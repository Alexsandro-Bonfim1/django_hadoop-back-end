# Django Hadoop Backend

A Django-based backend service for interacting with Hadoop ecosystem components including HDFS, Hive, and MapReduce jobs.

## Features

- HDFS File Management:
  - Upload files to HDFS
  - List directory contents
  - Delete files
  - File metadata management

- Hive Integration:
  - Execute Hive queries
  - Create tables from CSV files
  - List Hive tables
  - Query management

- Hadoop Job Management:
  - Submit MapReduce, Spark, Pig, and Hive jobs
  - Track job status
  - Kill running jobs
  - View job logs

- Monitoring:
  - Cluster health monitoring
  - HDFS capacity and usage tracking
  - MapReduce job metrics
  - YARN container metrics
  - Hive query metrics

## Prerequisites

- Python 3.8+
- Django 5.0+
- Hadoop cluster (HDFS, YARN, MapReduce)
- Hive Server
- Redis (for Celery)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Alexsandro-Bonfim1/django_hadoop-back-end.git
cd django_hadoop-back-end
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
- Copy `config.py.example` to `config.py`
- Update the configuration with your Hadoop cluster details

5. Initialize the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Initialize monitoring system:
```bash
python manage.py init_monitoring
```

## Running the Application

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A hadoop_project worker --loglevel=info
```

3. Start Celery beat (for periodic tasks):
```bash
celery -A hadoop_project beat --loglevel=info
```

4. Start Django development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- GET `/api-auth/login/` - Login
- GET `/api-auth/logout/` - Logout
- GET `/api-auth/user/` - Get current user

### HDFS Operations
- POST `/api/hdfs-files/upload/` - Upload file to HDFS
- GET `/api/hdfs-files/list_directory/` - List directory contents
- DELETE `/api/hdfs-files/{id}/` - Delete file

### Hive Operations
- POST `/api/hive-queries/execute/` - Execute Hive query
- POST `/api/hive-queries/create_table/` - Create table from CSV
- GET `/api/hive-queries/list_tables/` - List Hive tables

### Hadoop Job Operations
- POST `/api/hadoop-jobs/submit/` - Submit job
- GET `/api/hadoop-jobs/{id}/status/` - Get job status
- GET `/api/hadoop-jobs/{id}/logs/` - Get job logs
- POST `/api/hadoop-jobs/{id}/kill/` - Kill job

### Monitoring
- GET `/api/monitoring/cluster_health/` - Get cluster health
- GET `/api/monitoring/metrics/` - Get all metrics
- GET `/api/monitoring/hdfs_capacity/` - Get HDFS capacity
- GET `/api/monitoring/hdfs_usage/` - Get HDFS usage
- GET `/api/monitoring/mapreduce_jobs/` - Get MapReduce jobs
- GET `/api/monitoring/yarn_containers/` - Get YARN containers
- GET `/api/monitoring/hive_queries/` - Get Hive queries

## Configuration

The application can be configured through the `config.py` file. Key configuration options include:

```python
HADOOP_CONFIG = {
    'HDFS': {
        'host': 'localhost',
        'port': 50070,
        'user': 'hdfs',
        # ... other HDFS settings
    },
    'HIVE': {
        'host': 'localhost',
        'port': 10000,
        'user': 'hive',
        # ... other Hive settings
    },
    'MAPREDUCE': {
        'jobtracker': 'localhost:8088',
        'historyserver': 'localhost:19888',
        # ... other MapReduce settings
    },
    'MONITORING': {
        'cluster_health_check': {
            'interval': 300,
            'endpoints': {
                'namenode': 'http://localhost:50070/jmx',
                'resourcemanager': 'http://localhost:8088/jmx',
                'historyserver': 'http://localhost:19888/jmx'
            }
        }
    }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
