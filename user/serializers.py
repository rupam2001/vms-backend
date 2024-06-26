'''
Serializer for User API view
'''
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    '''Serializer for User model'''
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'id', 'created_at', 'is_active']
        extra_kwargs = {'password': {'write_only':  False, 'min_length': 8}}


    def create(self, validated_data):
        '''Create and return a new user'''
        password = validated_data.pop('password', None)
        user = get_user_model().objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
class UserOutSerializer(serializers.ModelSerializer):
    '''Serializer for User model'''
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'role', 'created_at']
    
class AuthTokenSerializer(serializers.Serializer):
    '''Serielaizer for user auth token'''
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input-type': 'password'},  #for css
        trim_whitespace=False
    )

    def validate(self, attrs):
        '''Validate and authenticate the user'''
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate to provided credentials')
            raise serializers.ValidationError(msg, code='authorization')  #will be catch by view
        
        attrs['user'] = user
        return attrs