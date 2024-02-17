from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from organization.serializers import OrganizationSerializer
from core.models import Visitor, User
from django.shortcuts import get_object_or_404
from visitor.serializers import VisitorSerializer

class VisitorViewSet(viewsets.ModelViewSet):
    '''View set to handle organization data'''
    serializer_class = VisitorSerializer
    queryset = Visitor.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    
    def create(self, request, *args, **kwargs):

        '''For initial creation'''

        print(self.request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        headers = self.get_success_headers(serializer.data)

        # Customize the response format
        response_data = {
            'success': True,
            'message': 'Visitor created successfully', 
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(methods=["GET"], detail=False)
    def suggested(self, request, *args, **kwargs):
        '''returns the suggested visitors for a user'''

        serializer = self.serializer_class(self.queryset.filter(created_by=self.request.user), many=True)
        headers = self.get_success_headers(serializer.data)

        # Customize the response format
        response_data = {
            'success': True,
            'message': f'found {len(serializer.data)} results.',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK, headers=headers)




