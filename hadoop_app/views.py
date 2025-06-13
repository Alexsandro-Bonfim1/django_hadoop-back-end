from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import HDFSFile, HiveQuery, HadoopJob, HadoopMetric
from .serializers import HDFSFileSerializer, HiveQuerySerializer, HadoopJobSerializer, HadoopMetricSerializer
from pyhive import hive
import hdfs
from datetime import datetime
import json
from .config import HADOOP_CONFIG, JOB_CONFIG_DEFAULTS
from .monitoring import hadoop_monitor

def get_hdfs_client():
    """Get configured HDFS client"""
    config = HADOOP_CONFIG['HDFS']
    return hdfs.InsecureClient(
        f'http://{config["host"]}:{config["port"]}',
        user=config["user"],
        timeout=config["timeout"]
    )

def get_hive_connection(database='default'):
    """Get configured Hive connection"""
    config = HADOOP_CONFIG['HIVE']
    return hive.Connection(
        host=config["host"],
        port=config["port"],
        username=config["user"],
        database=database,
        auth=config["auth"]
    )

class MonitoringViewSet(viewsets.ViewSet):
    """Viewset for monitoring Hadoop cluster health and metrics"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def cluster_health(self, request):
        """Get overall Hadoop cluster health"""
        health = hadoop_monitor.check_cluster_health()
        return Response(health)

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get Hadoop cluster metrics"""
        metrics = hadoop_monitor.collect_metrics()
        return Response(metrics)

    @action(detail=False, methods=['get'])
    def hdfs_capacity(self, request):
        """Get HDFS capacity metrics"""
        capacity = hadoop_monitor._get_hdfs_capacity()
        return Response(capacity)

    @action(detail=False, methods=['get'])
    def hdfs_usage(self, request):
        """Get HDFS usage metrics"""
        usage = hadoop_monitor._get_hdfs_used()
        return Response(usage)

    @action(detail=False, methods=['get'])
    def mapreduce_jobs(self, request):
        """Get MapReduce job metrics"""
        jobs = hadoop_monitor._get_mapreduce_jobs()
        return Response(jobs)

    @action(detail=False, methods=['get'])
    def yarn_containers(self, request):
        """Get YARN container metrics"""
        containers = hadoop_monitor._get_yarn_containers()
        return Response(containers)

    @action(detail=False, methods=['get'])
    def hive_queries(self, request):
        """Get Hive query metrics"""
        queries = hadoop_monitor._get_hive_queries()
        return Response(queries)

class HDFSFileViewSet(viewsets.ModelViewSet):
    queryset = HDFSFile.objects.all()
    serializer_class = HDFSFileSerializer
    permission_classes = [IsAuthenticated]

class HDFSFileViewSet(viewsets.ModelViewSet):
    queryset = HDFSFile.objects.all()
    serializer_class = HDFSFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HDFSFile.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        try:
            client = get_hdfs_client()
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            hdfs_path = f'/user/{request.user.username}/{file.name}'
            client.upload(hdfs_path, file)
            
            hdfs_file = HDFSFile.objects.create(
                name=file.name,
                path=hdfs_path,
                size=file.size,
                owner=request.user
            )
            
            return Response(HDFSFileSerializer(hdfs_file).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def list_directory(self, request):
        try:
            client = get_hdfs_client()
            path = request.query_params.get('path', f'/user/{request.user.username}')
            status = client.status(path, strict=False)
            
            if status:
                contents = client.list(path)
                return Response({
                    'path': path,
                    'exists': True,
                    'is_directory': status['type'] == 'DIRECTORY',
                    'contents': contents
                })
            else:
                return Response({
                    'path': path,
                    'exists': False
                })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        try:
            hdfs_file = get_object_or_404(HDFSFile, pk=pk, owner=request.user)
            client = get_hdfs_client()
            client.delete(hdfs_file.path, recursive=True)
            hdfs_file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_token(self, request):
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key})

    @action(detail=False, methods=['post'])
    def get_token_for_user(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username and password:
            user = get_object_or_404(User, username=username)
            if user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class HiveQueryViewSet(viewsets.ModelViewSet):
    queryset = HiveQuery.objects.all()
    serializer_class = HiveQuerySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HiveQuery.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['post'])
    def execute(self, request):
        """Execute a Hive query"""
        try:
            database = request.data.get('database', 'default')
            
            conn = get_hive_connection(database)
            cursor = conn.cursor()
            
            query = request.data.get('query')
            if not query:
                return Response({'error': 'No query provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            cursor.execute(query)
            
            result = cursor.fetchall()
            
            hive_query = HiveQuery.objects.create(
                query=query,
                result=str(result),
                owner=request.user,
                status='COMPLETED'
            )
            
            return Response(HiveQuerySerializer(hive_query).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def create_table(self, request):
        """Create a Hive table from a CSV file in HDFS"""
        try:
            table_name = request.data.get('table_name')
            hdfs_path = request.data.get('hdfs_path')
            columns = request.data.get('columns')
            
            if not all([table_name, hdfs_path, columns]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)
            
            conn = hive.Connection(host='localhost', port=10000, username='hive')
            cursor = conn.cursor()
            
            columns_str = ', '.join([f'{col} STRING' for col in columns])
            create_query = f"""
            CREATE TABLE {table_name} (
                {columns_str}
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
            LOCATION '{hdfs_path}'
            """
            
            cursor.execute(create_query)
            
            return Response({'message': f'Table {table_name} created successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_tables(self, request):
        """Get list of tables in a database"""
        try:
            database = request.query_params.get('database', 'default')
            
            conn = hive.Connection(host='localhost', port=10000, username='hive', database=database)
            cursor = conn.cursor()
            
            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()
            
            return Response({'tables': [t[0] for t in tables]})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HadoopJobViewSet(viewsets.ModelViewSet):
    queryset = HadoopJob.objects.all()
    serializer_class = HadoopJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HadoopJob.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit a Hadoop job"""
        try:
            config = request.data.get('configuration')
            if not config:
                return Response({'error': 'No configuration provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            job_type = config.get('type', 'HIVE').upper()
            
            if job_type not in ['MAPREDUCE', 'SPARK', 'PIG', 'HIVE']:
                return Response({'error': 'Invalid job type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get default configuration for job type
            default_config = JOB_CONFIG_DEFAULTS.get(job_type, {})
            
            # Merge default and user-provided configurations
            final_config = {**default_config, **config}
            
            job = HadoopJob.objects.create(
                name=config.get('name', 'Unnamed Job'),
                job_type=job_type,
                configuration=final_config,
                owner=request.user
            )
            
            # Simulate job submission
            job.status = 'SUBMITTED'
            job.save()
            
            return Response(HadoopJobSerializer(job).data, status=status.HTTP_201_CREATED)
            
            # Simulate job submission
            job.status = 'SUBMITTED'
            job.save()
            
            return Response(HadoopJobSerializer(job).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get job status"""
        try:
            job = get_object_or_404(HadoopJob, pk=pk, owner=request.user)
            return Response({'status': job.status})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get job logs"""
        try:
            job = get_object_or_404(HadoopJob, pk=pk, owner=request.user)
            # TODO: Implement actual log retrieval
            return Response({'logs': 'No logs available yet'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def kill(self, request, pk=None):
        """Kill a running job"""
        try:
            job = get_object_or_404(HadoopJob, pk=pk, owner=request.user)
            if job.status in ['RUNNING', 'SUBMITTED']:
                # TODO: Implement actual job killing
                job.status = 'KILLED'
                job.save()
                return Response({'message': 'Job killed successfully'})
            return Response({'error': 'Job is not in a state that can be killed'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
