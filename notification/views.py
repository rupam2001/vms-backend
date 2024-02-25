from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import InvitationPass, InvitationStatus, User, Visitor, INVITATION_STATUS, Belonging, Notification
from django.shortcuts import get_object_or_404
from invitation.serializers import InvitationPassINSerializer
from notification.serializers import NotificationSerializer
from core.utils import add_hours_to_utc
from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema
from django.db import transaction

import datetime
from datetime import timezone

from visitor.serializers import VisitorSerializer
from django.db.models import OuterRef, Subquery
from core import utils


class NotificationViewSet(viewsets.ModelViewSet):

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  

    @action(methods=['GET'], detail=False)
    def get_unread(self, request, *args, **kwargs):
        '''Get the unread notifications for the current authenticated user'''
        try:
            notification = self.queryset.filter(targeted_user=self.request.user, is_read=False)
            serialized = self.serializer_class(notification, many=True)
        except Notification.DoesNotExist:
            return Response(data={"success": True, "message":"No notification", "data":[]}, status=status.HTTP_200_OK)
        res = {
            "success": True,
            "message": "",
            "data": serialized.data
        }

        return Response(data=res, status=status.HTTP_200_OK)
    @action(methods=['PATCH'], detail=False)
    def mark_as_read(self, request, *args, **kwargs):
        '''Mark notifications as read'''
        notification_ids = request.data['notification_ids']
        self.queryset.filter(id__in=notification_ids).update(is_read=True)
        res = {
            "success": True,
            "message": "",
            "data": []
        }

        return Response(data=res, status=status.HTTP_200_OK)




    
    def list(self, request, *args, **kwargs):
        '''Return all the notifications belonging to the authenticated user'''
        super().list(request, *args, **kwargs)
        try:
            notification = self.queryset.filter(targeted_user=self.request.user)
            serialized = self.serializer_class(notification, many=True)
        except Notification.DoesNotExist:
            return Response(data={"success": True, "message":"No notification", "data":[]}, status=status.HTTP_200_OK)
        res = {
            "success": True,
            "message": "",
            "data": serialized.data
        }

        return Response(data=res, status=status.HTTP_200_OK)


    