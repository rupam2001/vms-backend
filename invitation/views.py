from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import InvitationPass, InvitationStatus, User, Visitor, INVITATION_STATUS, Belonging
from django.shortcuts import get_object_or_404
from invitation.serializers import InvitationPassINSerializer, InvitationPassOUTSerializer, InvitationPassOUTWithStatusSerializer
from core.utils import add_hours_to_utc
from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema
from django.db import transaction

import datetime
from datetime import timezone

from visitor.serializers import VisitorSerializer
from django.db.models import OuterRef, Subquery


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
        # Subquery to get the latest InvitationStatus created_at for each InvitationPass
        latest_status_created_at = InvitationStatus.objects.filter(
            invitation=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]

        invitations = self.queryset.filter(
            valid_from__date=date,
            invitationstatus__current_status__in=[
                INVITATION_STATUS.PENDING_APPROVAL,
                INVITATION_STATUS.READY_FOR_CHECKIN, 
                INVITATION_STATUS.APPROVED,
                INVITATION_STATUS.CHECKED_IN, 
                INVITATION_STATUS.CHECKED_OUT
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at)
        ).distinct()
            
        invitations = invitations.prefetch_related(
            Prefetch('belonging_set', queryset=Belonging.objects.all(), to_attr='belongings')
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
        try:
            with transaction.atomic():
                visitor_id = self.request.data.pop('visitor_id', None)
                if visitor_id is None:
                    return Response({}, status=status.HTTP_400_BAD_REQUEST)
                

                visitor = Visitor.objects.get(id=visitor_id)
                valid_till = add_hours_to_utc(request.data['valid_from'], 24)

                print("YO3", request.data)
                print(request.data['visiting_person_id'])

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
                    'message': 'Invitation created successfully',
                    'data': serializer.data
                }

                return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            response_data = {
                    'success': False,
                    'message': 'Something went wrong',
                    'data': {}
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

    @action(methods=['PATCH'], detail=True)
    def checkin(self, request, pk,  *args, **kwargs):
        '''Check in with belongings'''
        try:
            with transaction.atomic():

                invitation = self.queryset.get(id=pk)
                # add new status
                InvitationStatus.objects.create(
                    invitation=invitation,
                    current_status=INVITATION_STATUS.CHECKED_IN,
                    next_status=INVITATION_STATUS.CHECKED_OUT
                )

                #update the statuses in invitation pass to send it back
                invitation_serialized = self.serializer_class(invitation)
                #update the checkedin time
                setattr(invitation, 'checked_in_at', request.data['checked_in_at'])
                invitation.save()

                #add belongings
                belongings = request.data['belongings']

                Belonging.objects.bulk_create([Belonging(**data, invitation=invitation) for data in belongings])
                response_data = {
                    'success': True,
                    'message': 'Checked in successfull',
                    'data': invitation_serialized.data
                }


                return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_data = {
                    'success': False,
                    'message': 'Something went wrong',
                    'data': {}
            }
            print(e)
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['PATCH'], detail=True)
    def checkout(self, request, pk,  *args, **kwargs):
        '''Check in with belongings'''
        try:
            with transaction.atomic():

                invitation = self.queryset.get(id=pk)
                # add new status
                InvitationStatus.objects.create(
                    invitation=invitation,
                    current_status=INVITATION_STATUS.CHECKED_OUT,
                    next_status=INVITATION_STATUS.PENDING_REVIEW
                )

                #update the statuses in invitation pass to send it back
                invitation_serialized = self.serializer_class(invitation)
                #update the checkedin time
                setattr(invitation, 'checked_out_at', request.data['checked_out_at'])
                invitation.save()

                response_data = {
                    'success': True,
                    'message': 'Checked out successfull',
                    'data': invitation_serialized.data
                }


                return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_data = {
                    'success': False,
                    'message': 'Something went wrong',
                    'data': {}
            }
            print(e)
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)