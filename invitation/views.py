from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import InvitationPass, InvitationStatus, User, Visitor, INVITATION_STATUS, Belonging, Notification
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
from core import utils
import time


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
        current_date = utils.get_currenttime_utc()
        print(current_date)

        invitations = self.queryset.filter(
            visiting_person=self.request.user,
            invitationstatus__current_status__in=[INVITATION_STATUS.READY_FOR_CHECKIN, INVITATION_STATUS.APPROVED],
            valid_from__date__gt=current_date 
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
    def get_history(self, request, *args, **kwargs):
        '''Returns the upcoming invitation passes'''
        current_date = utils.get_currenttime_utc()
        print(current_date)

        invitations = self.queryset.filter(
            visiting_person=self.request.user,
            valid_from__date__lte=current_date,
            # invitationstatus__current_status__in=[INVITATION_STATUS.READY_FOR_CHECKIN, INVITATION_STATUS.APPROVED],

        ).order_by('-valid_from')

         # Prefetch InvitationStatus objects related to each InvitationPass
        invitations = invitations.prefetch_related(
            Prefetch('invitationstatus_set', queryset=InvitationStatus.objects.all(), to_attr='invitation_statuses')
        )


        for invitation in invitations:
            invitation.visitor = Visitor.objects.get(id=invitation.visitor_id)
            

        serializer = InvitationPassOUTWithStatusSerializer(data=invitations, many=True)
        serializer.is_valid()
        headers = self.get_success_headers(serializer.data)

        response_data = {
            'success': True,
            'message': '',
            'data': serializer.data
        }
        time.sleep(3)

        return Response(response_data, status=status.HTTP_200_OK, headers=headers)
    
    @action(methods=['GET'], detail=False)
    def get_requests(self, request, *args, **kwargs):
        '''Returns the upcoming invitation passes'''
        current_date = utils.get_currenttime_utc()
    
        latest_status_created_at = InvitationStatus.objects.filter(
            invitation=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]

        invitations = self.queryset.filter(
            valid_from__date=current_date,
            visiting_person=self.request.user,
            invitationstatus__current_status__in=[
                INVITATION_STATUS.PENDING_APPROVAL,
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at)
        ).distinct()

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
        time.sleep(3)
        return Response(response_data, status=status.HTTP_200_OK, headers=headers)

   
    @action(methods=['GET'], detail=False)
    def get_by_date(self, request, date,  *args, **kwargs):
        '''Returns the all the  visits in a perticular date [for SECURITY]'''
        # Subquery to get the latest InvitationStatus created_at for each InvitationPass
        latest_status_created_at = InvitationStatus.objects.filter(
            invitation=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]

        user_organization = request.user.orgnaization

        invitations = self.queryset.filter(
            valid_from__date=date,
            invitationstatus__current_status__in=[
                INVITATION_STATUS.PENDING_APPROVAL,
                INVITATION_STATUS.READY_FOR_CHECKIN, 
                INVITATION_STATUS.APPROVED,
                INVITATION_STATUS.CHECKED_IN, 
                INVITATION_STATUS.CHECKED_OUT
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at),
            visiting_person__orgnaization=user_organization
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
    def get_by_date_range(self, request,  *args, **kwargs):
        '''Returns the all the  visits in a perticular date [for SECURITY]'''
        # Subquery to get the latest InvitationStatus created_at for each InvitationPass
        latest_status_created_at = InvitationStatus.objects.filter(
            invitation=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]

        start_date = request.data['start_date']
        end_date = request.data['end_date']

        print(start_date, end_date)

        user_organization = self.request.user.orgnaization



        invitations = self.queryset.filter(
            valid_from__date__range=[start_date, end_date],
            invitationstatus__current_status__in=[
                INVITATION_STATUS.PENDING_APPROVAL,
                INVITATION_STATUS.READY_FOR_CHECKIN, 
                INVITATION_STATUS.APPROVED,
                INVITATION_STATUS.CHECKED_IN, 
                INVITATION_STATUS.CHECKED_OUT
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at),
            # visiting_person__orgnaization=user_organization  -- commented for testing purppose
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
                    visitor=visitor,
                    approver=self.request.user
                )
                headers = self.get_success_headers(serializer.data)

                InvitationStatus.objects.create(
                    invitation=InvitationPass.objects.get(id=serializer.data['id']),
                    current_status=INVITATION_STATUS.PENDING_APPROVAL,
                    comment="Visitor is ready to be approved",
                    next_status=INVITATION_STATUS.APPROVED
                )

                # create a notification
                Notification.objects.create(
                    targeted_user=visiting_person,
                    text=f"{visitor.first_name} {visitor.last_name} is waiting for your approval",
                    notification_type="Critical",
                    is_read=False
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
    
    @action(methods=['PATCH'], detail=True)
    def req_action(self, request, pk,  *args, **kwargs):
        '''For accept or reject of a invitation from the user side'''
        invitation = self.queryset.get(id=pk, visiting_person=self.request.user)
        action = self.request.data['action']
        if action  == INVITATION_STATUS.APPROVED:
            InvitationStatus.objects.create(
                invitation=invitation, 
                current_status=INVITATION_STATUS.APPROVED, 
                next_status=INVITATION_STATUS.READY_FOR_CHECKIN,
                comment="Invitation accepeted by the user"
            )
            InvitationStatus.objects.create(
                invitation=invitation, 
                current_status=INVITATION_STATUS.READY_FOR_CHECKIN, 
                next_status=INVITATION_STATUS.CHECKED_IN,
                comment="Ready for checkin"
            )
        elif action == INVITATION_STATUS.REJECTED:
            InvitationStatus.objects.create(
                invitation=invitation, 
                current_status=INVITATION_STATUS.REJECTED, 
                next_status=INVITATION_STATUS.UNKNOWN,
                comment="Invitation rejected by the user"
            )
           
        res = {
            "success": True,
            "message": "",
            "data":[]
        }
        return Response(data=res, status=status.HTTP_200_OK)

