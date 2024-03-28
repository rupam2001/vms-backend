from django.urls import path
from .views import get_qrcode, varify_and_pair_device, checkPairConn, validate_pass_key

urlpatterns = [
    path('get_pairing_qrcode/', get_qrcode, name='get_qrcode'),
    path("pair_device/", varify_and_pair_device, name="pair_device"),
    path("check_pair_conn/", checkPairConn, name='checkPairConn'),
    path("check_pair_conn/", checkPairConn, name='check_pair_conn'),
    path("varify_qr/", validate_pass_key, name='validate_passkey')
    # Add other URL patterns as needed
]
