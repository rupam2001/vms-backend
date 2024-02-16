from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from core.models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    '''Serailizer to handle organization model'''
    class Meta:
        model = Organization
        fields = ['id','name', 'email', 'about']
        read_only_fields = ['id']

    def create(self, validated_data):
        '''create a new organization'''
        organization = Organization.objects.create(**validated_data)
        return organization
    


class OrganizationWithDetailSerializer(serializers.Serializer):
    '''Custom Serializer to handle organization model'''

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    about = serializers.CharField()
    members_count =  serializers.SerializerMethodField(method_name='get_members_count')

    def get_members_count(self, obj):
        return obj.members.count()


    def create(self, validated_data):
        '''Create a new organization'''
        return Organization.objects.create(**validated_data)
