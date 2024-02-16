from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organization import views

router = DefaultRouter()
router.register('', viewset=views.OrganizationViewSet)  #it creates all the routes for CRUD from the ViewSet, since we are using ModelViewSet this fuctions are available by default

app_name = 'organization'

urlpatterns = [
    path('/', include(router.urls))
]
