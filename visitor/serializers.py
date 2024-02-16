from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from core.models import Visitor

class VisitorSerializer(serializers.ModelSerializer):
    '''Serailizer to handle organization model'''
    class Meta:
        model = Visitor
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'address', 'company']
        read_only_fields = ['id']

    def create(self, validated_data):
        '''create a new visitor'''
        organization = Visitor.objects.create(**validated_data)
        return organization 