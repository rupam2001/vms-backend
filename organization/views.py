from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from organization.serializers import OrganizationSerializer
from core.models import Organization, User
from django.shortcuts import get_object_or_404
from user.serializers import UserSerializer



class OrganizationViewSet(viewsets.ModelViewSet):
    '''View set to handle organization data'''
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  

    # def perform_create(self, serializer):
    #     '''Create a new Organization'''
    #     serializer.save(created_by=self.request.user)
    #     print('Organization created')
    
    def create(self, request, *args, **kwargs):

        '''For initial creation'''

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        headers = self.get_success_headers(serializer.data)

        # Customize the response format
        response_data = {
            'success': True,
            'message': 'Organization created successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    def partial_update(self, request, *args, **kwargs):
        '''Handle partial updates for an organization'''
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)

        # Customize the response format
        response_data = {
            'success': True,
            'message': 'Organization updated successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def user_organization(self, request, pk=None):
        '''Get the organization belongs to the specified user/owner'''
        user = self.request.user
        organization = get_object_or_404(Organization, created_by=user)
        serializer = self.serializer_class(organization)

        
        # serializer.data['users_count'] = User.objects.filter(organization=organization).count()

        # members_serializer = UserSerializer(organization.members.all(), many=True)
        # serializer.data['members'] = members_serializer.data


        print(serializer.data)

        headers = self.get_success_headers(serializer.data)
        response_data = {
            'success': True,
            'message': '',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['GET'])
    def organization_stats(self, request, pk=None):
        '''Get the meta data and stats for a particular organization'''
        user = self.request.user
        organization = get_object_or_404(Organization, created_by=user)
        serializer = self.serializer_class(organization)
        serializer.data['users_count'] = user.organization.count() 
        headers = self.get_success_headers(serializer.data)


        response_data = {
            'success': True,
            'message': '',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['GET'])
    def get_users(self, request, pk=None):
        '''Get the meta data and stats for a particular organization'''
        user = self.request.user
        organization = get_object_or_404(Organization, created_by=user)
        user_list =  UserSerializer(organization.user_set.all(), many=True)
        serializer = self.serializer_class(organization)



        headers = self.get_success_headers(serializer.data)

        response_data = {
            'success': True,
            'message': '',
            'data': user_list.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)



    def get_queryset(self):
        return self.queryset
    
    def get_serializer_class(self):
        return self.serializer_class

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response({'message': 'Organization updated successfully'}, status=status.HTTP_200_OK)