from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/realtime_invitations/', consumers.RealtimeInvitaionsConsumer.as_asgi())
]