from django.urls import path

from bookrapi.core import consumers

websocket_patterns = [
    path('ws/chat/<room_name>/', consumers.CrawlerConsumer)
]