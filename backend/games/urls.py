from django.urls import path

from . import views

urlpatterns = [
    path("join/", views.WaitingRoomJoinView.as_view(), name="waiting-room-join"),
    path("leave/", views.WaitingRoomLeaveView.as_view(), name="waiting-room-leave"),
]
