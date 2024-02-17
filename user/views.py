from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from organization.serializers import OrganizationSerializer
from core.models import Organization

from rest_framework.decorators import action
from rest_framework import viewsets
from core.models import User
from django.shortcuts import get_object_or_404

from django.db import models



class CreateUserView(generics.CreateAPIView):
    '''To create a new user'''
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  

    def create(self, request, *args, **kwargs):

        '''User creation by the owner'''
        user_serializer = self.get_serializer(data=request.data)
        print(request.data)
        user_serializer.is_valid(raise_exception=True)
        org = Organization.objects.get(created_by=request.user)
        # print(org)
        user_serializer.save(orgnaization=org)
        
        # self.perform_create(serializer)
        headers = self.get_success_headers(user_serializer.data)

        # Customize the response format
        response_data = {
            'success': True,
            'message': 'User created successfully',
            'data': user_serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    

class CreateOwnerView(generics.CreateAPIView):
    '''API view for Owner creation'''
    serializer_class = UserSerializer


    def create(self, request, *args, **kwargs):
        '''For owener creation'''
        request.data['role'] = 'OWNER'
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Customize the response format
        response_data = {
            'success': True,
            'message': 'User created successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

class CreateTokenView(ObtainAuthToken):
    '''Create a auth token for user'''
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # for UI purpose only

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)


        # Customize the response format
        response_data = {
            'success': True,
            'message': 'User authenticated successfully',
            'data': {'token': token.key, 'role': user.role}
        }

        return Response(response_data, status=status.HTTP_200_OK)


class MangeUserViewSets(viewsets.ModelViewSet):
    '''Manage Authenticated user'''
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        '''Retrieve and retrun the authenticated user.'''
        return self.request.user
        
    @action(detail=False, methods=['GET'])
    def details(self, request, pk=None):
        '''Return the user object'''
       
        user = self.get_object()
        
        # Use self.serializer_class to create an instance of the serializer with the user instance
        serialized_user = self.serializer_class(user)
        headers = self.get_success_headers(serialized_user.data)
        notifications = user.notification_set.all()
        print(notifications)

        response_data = {
            'success': True,
            'message': '',
            'data': serialized_user.data
        }

        return Response(response_data, status=status.HTTP_200_OK, headers=headers)
    
    @action(detail=False, methods=['POST'])
    def search(self, request, *args, **kwargs):
        '''returns the user with search query match'''
        query = self.request.data['query']
        print(query)
        if query:
            # Search for users with matching first name, last name, or email
            if len(query.split(" ")) == 2:
                users = User.objects.filter(
                    models.Q(first_name__icontains=query) |
                    models.Q(last_name__icontains=query) |
                    models.Q(first_name__icontains=query.split()[0])|
                    models.Q(last_name__icontains=query.split()[1])|
                    models.Q(email__icontains=query)
                )
            else:
                users = User.objects.filter(
                    models.Q(first_name__icontains=query) |
                    models.Q(last_name__icontains=query) |
                    models.Q(email__icontains=query)
                )
         
            serailizer = UserSerializer(users, many=True)
            response_data = {
            'success': True,
            'message': '',
            'data': serailizer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
    
        


    
    def get_queryset(self):
        return self.queryset
    
    def get_serializer_class(self):
        return self.serializer_class


class UserView(generics.CreateAPIView):
    '''API for User related RUD'''
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  


    def retrieve(self, request, *args, **kwargs):
        '''Get details of the current authenticated user'''
        user = request.user
        serializer = self.get_serializer(request.user)

        headers = self.get_success_headers(serializer.data)

        response_data = {
            'success': True,
            'message': '',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK, headers=headers)


