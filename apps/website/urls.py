from django.urls import path

from .views import *


urlpatterns = [
    path("privacy-policy.html", privacy_policy_view),
]
