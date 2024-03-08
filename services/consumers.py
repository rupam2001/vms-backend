
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer, AsyncJsonWebsocketConsumer
import json
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("connected ws")
       

    async def disconnect(self, close_code):
        print("dissconnected ws", close_code)
        pass
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.send(text_data=json.dumps({
            'message': message
        }))



from channels.generic.websocket import AsyncWebsocketConsumer
import json
from confluent_kafka import Consumer, KafkaError
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from core.models import User

import asyncio
# import aioredis


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        token = headers.get(b"authorization", b"").decode("utf-8").split(" ")[1]
        print(token, "AuthMiddleware channels token")

        #use the token to get the user data
        
        payload = {'user_id': ''}
        scope["user"] = await self.get_user(payload["user_id"])
      

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)


class RealtimeInvitaionsConsumer(AsyncWebsocketConsumer):
    '''Consumes realtime messages and sends them to corressponding subscriber'''
    async def connect(self):
        await self.accept()
        print(self.scope['user'])
        return
        # Get the user-specific channel name
        user_channel = self.scope['user'].username if 'user' in self.scope else 'default_user'
         
        # Connect to Redis with the specified URL
        self.redis = await aioredis.create_redis('redis://:foobared@192.168.1.8:6379' )
        # Subscribe to the user-specific channel
        self.redis_sub = await self.redis.subscribe(user_channel)
        asyncio.ensure_future(self.send_redis_messages())
      

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        self.send(text_data=json.dumps({
            'message': message
        }))

      

