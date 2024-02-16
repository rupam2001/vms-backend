from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from core.models import InvitationPass, InvitationStatus

class InvitationPassINSerializer(serializers.ModelSerializer):
    '''Serailizer to handle InvitationPass model'''
    class Meta:
        model = InvitationPass
        fields = [
            'id', 'valid_from', 'valid_till', 'purpose',  
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'valid_till': {'required': False}
        }

    def create(self, validated_data):
        '''create a new invitation pass'''
        organization = InvitationPass.objects.create(**validated_data)
        return organization 
    

