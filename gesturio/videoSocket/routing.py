from django.urls import re_path
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/video/", consumers.VideoConsumer.as_asgi()),
]