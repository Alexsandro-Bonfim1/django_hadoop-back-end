from rest_framework import serializers
from .models import HDFSFile, HiveQuery, HadoopJob, HadoopMetric

class HDFSFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HDFSFile
        fields = '__all__'

class HiveQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = HiveQuery
        fields = '__all__'

class HadoopJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = HadoopJob
        fields = '__all__'

class HadoopMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = HadoopMetric
        fields = '__all__'
