from django.urls import path

from .views import EventDetail, EventIndex

app_name = "events"

urlpatterns = [
    path("", EventIndex.as_view(), name="index"),
    path("<slug:slug>/", EventDetail.as_view(), name="detail"),
]
