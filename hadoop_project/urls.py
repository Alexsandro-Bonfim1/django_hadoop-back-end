"""
URL configuration for hadoop_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hadoop_app.views import HDFSFileViewSet, HiveQueryViewSet, HadoopJobViewSet, MonitoringViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'hdfs-files', HDFSFileViewSet)
router.register(r'hive-queries', HiveQueryViewSet)
router.register(r'hadoop-jobs', HadoopJobViewSet)
router.register(r'monitoring', MonitoringViewSet, basename='monitoring')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
