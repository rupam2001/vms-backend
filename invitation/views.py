from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import InvitationPass, InvitationStatus, User, Visitor, INVITATION_STATUS
from django.shortcuts import get_object_or_404
from invitation.serializers import InvitationPassINSerializer, InvitationPassOUTSerializer, InvitationPassOUTWithStatusSerializer
from core.utils import add_hours_to_utc
from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema



from visitor.serializers import VisitorSerializer

class InvitationPassViewSet(viewsets.ModelViewSet):
    '''View set to handle organization data'''
    serializer_class = InvitationPassINSerializer
    queryset = InvitationPass.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    
    def create(self, request, *args, **kwargs):

        '''For creating invitation pass'''
        print(self.request.data)
        visitor_id = self.request.data.pop('visitor_id', None)
        if visitor_id is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        visitor = Visitor.objects.get(id=visitor_id)
        valid_till = add_hours_to_utc(request.data['valid_from'], 24)

        print(request.data)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        serializer.save(
            valid_till=valid_till,
            created_by=self.request.user,
            visiting_person=self.request.user,
            visitor=visitor
        )
        headers = self.get_success_headers(serializer.data)

        InvitationStatus.objects.create(
            invitation=InvitationPass.objects.get(id=serializer.data['id']),
            current_status=INVITATION_STATUS.READY_FOR_CHECKIN,
            comment="Visitor is ready to checked in",
            next_status=INVITATION_STATUS.CHECKED_IN
        )
        
        # Customize the response format
        response_data = {
            'success': True,
            'message': 'Invitiation pass created successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(methods=['GET'], detail=False)
    def get_upcomming(self, request, *args, **kwargs):
        '''Returns the upcoming invitation passes'''
        invitations = self.queryset.filter(
            visiting_person=self.request.user,
            invitationstatus__current_status__in=[INVITATION_STATUS.READY_FOR_CHECKIN, INVITATION_STATUS.APPROVED]
        )

         # Prefetch InvitationStatus objects related to each InvitationPass
        invitations = invitations.prefetch_related(
            Prefetch('invitationstatus_set', queryset=InvitationStatus.objects.all(), to_attr='invitation_statuses')
        )


        for invitation in invitations:
            invitation.visitor = Visitor.objects.get(id=invitation.visitor_id)
            

        serializer = InvitationPassOUTSerializer(data=invitations, many=True)
        serializer.is_valid()
        headers = self.get_success_headers(serializer.data)

        response_data = {
            'success': True,
            'message': '',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK, headers=headers)

   
    @action(methods=['GET'], detail=False)
    def get_by_date(self, request, date,  *args, **kwargs):
        '''Returns the all the  visits in a perticular date [for SECURITY]'''
        print(date)
        invitations = self.queryset.filter(
            valid_from__date=date,
            invitationstatus__current_status__in=[
                INVITATION_STATUS.READY_FOR_CHECKIN, INVITATION_STATUS.APPROVED,
                INVITATION_STATUS.CHECKED_IN, INVITATION_STATUS.CHECKED_OUT,
                INVITATION_STATUS.PENDING_APPROVAL
            ]
        )
            
        serializer = InvitationPassOUTWithStatusSerializer(data=invitations, many=True)
        serializer.is_valid()
        headers = self.get_success_headers(serializer.data)

        response_data = {
            'success': True,
            'message': '',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK, headers=headers)
    
    @action(methods=['POST'], detail=False)
    def create_by_security(self, request, *args, **kwargs):

        '''For creating invitation pass'''
        print(self.request.data)
        visitor_id = self.request.data.pop('visitor_id', None)
        if visitor_id is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        visitor = Visitor.objects.get(id=visitor_id)
        valid_till = add_hours_to_utc(request.data['valid_from'], 24)

        visiting_person = User.objects.get(id=request.data['visiting_person_id'])

        print(request.data)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        serializer.save(
            valid_till=valid_till,
            created_by=self.request.user,
            visiting_person=visiting_person,
            visitor=visitor
        )
        headers = self.get_success_headers(serializer.data)

        InvitationStatus.objects.create(
            invitation=InvitationPass.objects.get(id=serializer.data['id']),
            current_status=INVITATION_STATUS.PENDING_APPROVAL,
            comment="Visitor is ready to be approved",
            next_status=INVITATION_STATUS.APPROVED
        )
        
        # Customize the response format
        response_data = {
            'success': True,
            'message': 'Invitiation pass created successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)