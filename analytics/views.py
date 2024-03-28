from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication


from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import InvitationPass, InvitationStatus, User, Visitor, INVITATION_STATUS, Belonging, Notification
from django.shortcuts import get_object_or_404
from invitation.serializers import InvitationPassINSerializer, InvitationPassOUTSerializer, InvitationPassOUTWithStatusSerializer
from core.utils import add_hours_to_utc
from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema

import datetime
from datetime import timezone

from visitor.serializers import VisitorSerializer
from django.db.models import OuterRef, Subquery
from core import utils



class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    '''View set to provide all the data for analytics'''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    queryset = InvitationPass.objects.all()
    
    @action(methods=['POST'], detail=False)
    def get_metrics(self, request, *args, **kwargs):
        '''
            Returns the data for metrics section in the analytic section
            Metrics:
                1. Total visits, 
                2. Total visitors, 
                3. Total walkin visits, 
                4. Total Invited visits
        '''

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
                INVITATION_STATUS.CHECKED_OUT
                
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at),
            # visiting_person__orgnaization=user_organization #commented for testing purppose
        ).distinct()

        serializer = InvitationPassOUTSerializer(data=invitations, many=True)
        serializer.is_valid()

    
     
        total_visitors = set()
        total_walkin_visits = len(list(filter(lambda i: i.approver != None, invitations)))
        for i in invitations:
            total_visitors.add(i.visitor.id)



        data = {
            "total_visits": len(invitations),
            "total_visitors": len(total_visitors),
            "total_walkin_visits": total_walkin_visits,
            "total_invited_visits": len(invitations) - total_walkin_visits
            # "invitations": serializer.data
        }
        response = {
            "success": True,
            "message": "",
            "data": data
        }

        return Response(data=response, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False)
    def get_visitors_month(self, request, *args, **kwargs):
        '''
            Returns the count of visits for each month
        '''

        latest_status_created_at = InvitationStatus.objects.filter(
            invitation=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]

       

        year = request.data['currYear']

        print(year)

        user_organization = self.request.user.orgnaization

        invitations = self.queryset.filter(
            valid_from__year=year,
            invitationstatus__current_status__in=[
                # INVITATION_STATUS.CHECKED_IN,
                INVITATION_STATUS.CHECKED_OUT
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at),
            # visiting_person__orgnaization=user_organization #commented for testing purppose
        ).distinct()

        serializer = InvitationPassOUTSerializer(data=invitations, many=True)
        serializer.is_valid()

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        counts = [0 for _ in range(0, len(months))]
        for i in invitations:
            month = i.valid_from.month
            counts[month - 1] += 1
        

        data = {
            month: count for month, count in zip(months, counts)
        }
        

        response = {
            "success": True,
            "message": "",
            "data": data
        }

        return Response(data=response, status=status.HTTP_200_OK)
    

    @action(methods=['POST'], detail=False)
    def get_summary_table(self, request, *args, **kwargs):
        '''
            Returns the data for summary table
            visitor name,
            visiting person name,
            visiting person email
            checkin at
            check out at
            email
            phone
            address
            purpose
            feedback
            rating
        '''

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
                # INVITATION_STATUS.CHECKED_IN,
                INVITATION_STATUS.CHECKED_OUT
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at),
            # visiting_person__orgnaization=user_organization #commented for testing purppose
        ).distinct()


        invitations = invitations.prefetch_related(
            Prefetch('invitationstatus_set', queryset=InvitationStatus.objects.all(), to_attr='invitationstatuses')
        )
        

        serializer = InvitationPassOUTWithStatusSerializer(data=invitations, many=True)
        serializer.is_valid()
        

        table = []
        for i in invitations:
           
            print(i.invitationstatuses, "inv status")
            checkin = list(filter(lambda x: x.current_status == INVITATION_STATUS.CHECKED_IN, i.invitationstatuses))[0]
            checkout = list(filter(lambda x: x.current_status == INVITATION_STATUS.CHECKED_OUT, i.invitationstatuses))[0]
            row = {}
            row['name'] = f'{i.visitor.first_name} {i.visitor.last_name}'
            row['visiting_person_name'] = f'{i.visiting_person.first_name} {i.visiting_person.last_name}'
            row['visting_person_email'] = i.visiting_person.email
            row['check_in_at'] = checkin.created_at#
            row['check_out_at'] = checkout.created_at #
            row['email'] = i.visitor.email
            row['phone'] = i.visitor.phone
            row['address'] = i.visitor.address
            row['purpose'] = i.purpose
            row['feedback'] = i.feedback 
            row['rating'] = i.rating
            table.append(row)

        

        response = {
            "success": True,
            "message": "",
            "data": table
        }

        return Response(data=response, status=status.HTTP_200_OK)


    
    @action(methods=['POST'], detail=False)
    def get_visitors_by_day(self, request, *args, **kwargs):
        '''
            Returns the data for visitir by day
            @NOT_IN_USE

        '''

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
                # INVITATION_STATUS.CHECKED_IN,
                INVITATION_STATUS.CHECKED_OUT
            ],
            invitationstatus__created_at=Subquery(latest_status_created_at),
            # visiting_person__orgnaization=user_organization #commented for testing purppose
        ).distinct()


        invitations = invitations.prefetch_related(
            Prefetch('invitationstatus_set', queryset=InvitationStatus.objects.all(), to_attr='invitationstatuses')
        )
        

        serializer = InvitationPassOUTWithStatusSerializer(data=invitations, many=True)
        serializer.is_valid()
        

        table = []
        for i in invitations:
           
            print(i.invitationstatuses, "inv status")
            checkin = list(filter(lambda x: x.current_status == INVITATION_STATUS.CHECKED_IN, i.invitationstatuses))[0]
            checkout = list(filter(lambda x: x.current_status == INVITATION_STATUS.CHECKED_OUT, i.invitationstatuses))[0]
            row = {}
            row['name'] = f'{i.visitor.first_name} {i.visitor.last_name}'
            row['visiting_person_name'] = f'{i.visiting_person.first_name} {i.visiting_person.last_name}'
            row['visting_person_email'] = i.visiting_person.email
            row['check_in_at'] = checkin.created_at#
            row['check_out_at'] = checkout.created_at #
            row['email'] = i.visitor.email
            row['phone'] = i.visitor.phone
            row['address'] = i.visitor.address
            row['purpose'] = i.purpose
            row['feedback'] = i.feedback 
            row['rating'] = i.rating
            table.append(row)

        

        response = {
            "success": True,
            "message": "",
            "data": table
        }

        return Response(data=response, status=status.HTTP_200_OK)



        
            
        



