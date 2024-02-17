from django.urls import path, include
from rest_framework.routers import DefaultRouter
from invitation import views

router = DefaultRouter()
router.register('', viewset=views.InvitationPassViewSet)  #it creates all the routes for CRUD from the ViewSet, since we are using ModelViewSet this fuctions are available by default

app_name = 'invitation'

urlpatterns = [
    path('/', include(router.urls)),
    path('/get_by_date/<str:date>', views.InvitationPassViewSet.as_view({'get': 'get_by_date'}), name='get_by_date_invitations'),

]
