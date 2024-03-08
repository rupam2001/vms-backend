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
import math
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
import secrets
from django.conf import settings
import redis
import json

#initialize redis connection







# Create your views here.

class ServicesViewSet(APIView):
    '''To handle different general purpose services'''
    pass
    


store = {}



redis_store = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_qrcode(request, *args, **kwargs):
    '''returns the qr code to pair a device'''
    #create a qr code against the requestor and store it somewhere
    time.sleep(1.5)
    

    
    random_token = secrets.token_hex(16)
    data = {
        "token": random_token,
        "created_at": int(round(time.time() * 1000)),
        "email": request.user.email
    }
    redis_store.set(random_token, json.dumps(data))
    expiration_time = 3600 * 12# expire name
    redis_store.expire(random_token, expiration_time)


    response = {
        "success": True,
        "message": "",
        "data": {
            "token":random_token
        }

    }
    print(random_token) #30d35c4d9fc7de464e950969cb8d1669
    # Your logic for generating and returning the QR code
    return Response(data=response, status=200)


def search_token_in_store(store, token):
    """
    Search for an element inside the values of a dictionary.
    Returns the key where the element is found.
    """
    for key, value in store.items():
        if token in value['token']:
            return key, True  # Element found
    return None, False  # Element not found

@api_view(['POST'])
def varify_and_pair_device(request, *args, **kwargs):
    '''varify the qr code'''
    token = request.data['token']
    print(token)

    data = redis_store.get(token)
    if data:
        #create a token for the device which the device has to send this token everytime when it scanes
        device_token = secrets.token_hex(16)
        print(data)
        data = json.loads(data)

        redis_store.set(device_token, json.dumps({
            "email": data['email'],
            "created_at": int(round(time.time() * 1000)),
            "device_name": token[:5]
        }))
        expiration_time = 3600 * 12 # expire name
        redis_store.expire(device_token, expiration_time)

        

        response = {
            "success": True,
            "message":"",
            "data":{
                "token": device_token  # 
            }
        }


        return Response(data=response, status=status.HTTP_200_OK)
    
    return Response(data=None, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def checkPairConn(request, *args, **kwargs):
    '''returns the status of the device token'''
    device_token = request.data['device_token']
    if not device_token:
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)
    res = redis_store.get(device_token)
    response = {
        "success": True,
        "message":"",
        "data":{}
    }
    if res:
        response['data'] = { "valid": True}
        return Response(data=response, status=status.HTTP_200_OK)
    
    if not res:
        response['data'] = {'valid': False}
        return Response(data=response, status=status.HTTP_200_OK)
    
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def validate_pass_key( request, *args, **kwargs):
    '''validedates the passkey for a temporary duration of time '''
    device_token = request.data['device_token']
    device_data = redis_store.get(device_token)

    print(device_token, "device token")
    print(device_data, "device data")

    if not device_data:
        #device token is not valid or expired
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)
    

    passkey = request.data['passkey']
    invitation = InvitationPass.objects.get(passkey=passkey)
    if not invitation:
        return Response(data={}, status=status.HTTP_404_NOT_FOUND)
    
    device_data = json.loads(device_data) 
    data = {
        'created_at': int(round(time.time() * 1000)),
        'email': device_data['email']  #email of the security who scanned the passkey
    }
    
    redis_store.set(passkey, json.dumps(data))
    expiration_time = 3600 # expire name of the passkey scanning
    redis_store.expire(device_token, expiration_time)

    print("Scanned!")

    return Response(data={
        "success": True,
        "message":"",
        "data":{}
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_websocket_token(request, *args, **kwargs):
    '''Returns a temporary token which can be used to connect with realtime websocket endpoints'''
    pass

        
