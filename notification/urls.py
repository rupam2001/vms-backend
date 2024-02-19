from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notification import views

router = DefaultRouter()
router.register('', viewset=views.NotificationViewSet)  #it creates all the routes for CRUD from the ViewSet, since we are using ModelViewSet this fuctions are available by default

app_name = 'notification'

urlpatterns = [
    path('/', include(router.urls)),
]
