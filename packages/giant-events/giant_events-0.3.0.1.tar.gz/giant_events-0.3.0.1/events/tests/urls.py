from django.urls import include, path

""""
Url patterns for testing
"""

urlpatterns = [path("events/", include("events.urls", namespace="events"))]
