from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import InvitationPass, InvitationStatus, User, Visitor, INVITATION_STATUS
from django.shortcuts import get_object_or_404
from invitation.serializers import InvitationPassINSerializer
from core.utils import add_hours_to_utc


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
        print(request.data['valid_from'], valid_till)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
    