from django.contrib import admin
from django.urls import path,include
from videoSocket import views
urlpatterns = [
    path('', views.index, name='index'),
]

