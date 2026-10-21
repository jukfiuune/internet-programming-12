import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import waiting_room

logger = logging.getLogger(__name__)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"


class WaitingRoomJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            waiting_room.join(request.user)
        except waiting_room.WaitingRoomError as exc:
            raise Conflict(str(exc))

        try:
            game = waiting_room.form_game()
        except (waiting_room.WaitingRoomError, IntegrityError):
            logger.exception("Forming a game from the waiting room failed")
            game = None

        if game is not None and game.players.filter(user=request.user).exists():
            return Response({"waiting": False, "game": game.id}, status=status.HTTP_201_CREATED)
        return Response({"waiting": True}, status=status.HTTP_201_CREATED)


class WaitingRoomLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not waiting_room.leave(request.user):
            raise NotFound("You are not in the waiting room.")
        return Response(status=status.HTTP_204_NO_CONTENT)
