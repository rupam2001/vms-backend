from django.urls import path, include
from user import views

app_name = 'user' 

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('', viewset=views.MangeUserViewSets)  #it creates all the routes for CRUD from the ViewSet, since we are using ModelViewSet this fuctions are available by default

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name='create'),
    path('owner/', views.CreateOwnerView.as_view(), name="owner"),
    path("login/", views.CreateTokenView.as_view(), name='login'),
    # path("me/", views.MangeUserView.as_view(), name="me"),
    path('me/', include(router.urls))
    
]