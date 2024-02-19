from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from core.models import InvitationPass, InvitationStatus, Belonging, Notification
from visitor.serializers import VisitorSerializer
from user.serializers import UserSerializer, UserOutSerializer


class NotificationSerializer(serializers.ModelSerializer):
    '''Serailizer for notification'''
    class Meta:
        model = Notification
        fields = [
            'id', 'targeted_user', 'text', 'created_at', 'is_read' 
        ]
        read_only_fields = ['id']
        # extra_kwargs = {
        #     'valid_till': {'required': False}
        # }

