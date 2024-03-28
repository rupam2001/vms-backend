from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from core.models import InvitationPass, InvitationStatus, Belonging
from visitor.serializers import VisitorSerializer
from user.serializers import UserSerializer, UserOutSerializer

class InvitationPassINSerializer(serializers.ModelSerializer):
    '''Serailizer to handle InvitationPass model'''
    # visitor = VisitorSerializer()  
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
    
class InvitationPassOUTSerializer(serializers.ModelSerializer):
    '''Serailizer to handle InvitationPass model'''
    visitor = VisitorSerializer()  
    class Meta:
        model = InvitationPass
        fields = [
            'id', 'valid_from', 'valid_till', 'purpose', 'visitor'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'valid_till': {'required': False},
            'visitor': {'required': False}
        }

    def create(self, validated_data):
        '''create a new invitation pass'''
        organization = InvitationPass.objects.create(**validated_data)
        return organization 
    

class InvitationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationStatus
        fields = ['id', 'current_status', 'next_status', 'comment', 'created_at']

class BelongingSerializer(serializers.ModelSerializer):
    '''Serializer for belongings'''
    class Meta:
        model = Belonging
        fields = ['id', 'description', 'name', 'identifier_code']
        read_only_fields = ['id']


class InvitationPassOUTWithStatusSerializer(serializers.ModelSerializer):
    '''Serailizer to handle InvitationPass model'''
    visitor = VisitorSerializer()  
    invitationstatus_set = InvitationStatusSerializer(many=True, read_only=True)
    belongings = BelongingSerializer(many=True, read_only=True)
    visiting_person = UserOutSerializer()
    class Meta:
        model = InvitationPass
        fields = [
            'id', 'valid_from', 'valid_till', 'purpose', 'visitor', 'invitationstatus_set', 'visiting_person',
            'checked_in_at', 'checked_out_at', 'belongings', "passkey"
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            
        }

    def create(self, validated_data):
        '''create a new invitation pass'''
        organization = InvitationPass.objects.create(**validated_data)
        return organization 

