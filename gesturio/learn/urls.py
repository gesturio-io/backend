from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('category', CategoryFetch.as_view(), name='category-fetch'),
]
