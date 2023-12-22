from django.urls import path

from .views import *


urlpatterns = [
    path("privacy-policy/", privacy_policy_view),
]
