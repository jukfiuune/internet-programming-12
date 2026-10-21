import random

from django.db import IntegrityError, transaction

from .models import Game, GamePlayer, WaitingRoomEntry

PLAYERS_PER_GAME = 3
BUSY_STATUSES = [Game.WAITING, Game.IN_PROGRESS]


class WaitingRoomError(Exception):
    pass


class AlreadyWaiting(WaitingRoomError):
    pass


class NotEligible(WaitingRoomError):
    pass


def busy_user_ids():
    return GamePlayer.objects.filter(game__status__in=BUSY_STATUSES).values("user_id")


def is_eligible(user):
    return not GamePlayer.objects.filter(user=user, game__status__in=BUSY_STATUSES).exists()


def join(user):
    if not is_eligible(user):
        raise NotEligible("You are already playing in a waiting or active game.")
    try:
        with transaction.atomic():
            return WaitingRoomEntry.objects.create(user=user)
    except IntegrityError:
        raise AlreadyWaiting("You are already in the waiting room.")


def leave(user):
    deleted, _ = WaitingRoomEntry.objects.filter(user=user).delete()
    return deleted > 0


@transaction.atomic
def form_game():
    eligible = list(
        WaitingRoomEntry.objects.select_for_update()
        .exclude(user_id__in=busy_user_ids())
        .select_related("user")
    )
    if len(eligible) < PLAYERS_PER_GAME:
        return None

    chosen = random.sample(eligible, PLAYERS_PER_GAME)
    colors = random.sample([value for value, _ in GamePlayer.COLOR_CHOICES], PLAYERS_PER_GAME)

    game = Game.objects.create(created_by=chosen[0].user, status=Game.WAITING)
    for order, (entry, color) in enumerate(zip(chosen, colors), start=1):
        GamePlayer.objects.create(game=game, user=entry.user, player_order=order, color=color, score=0)

    deleted, _ = WaitingRoomEntry.objects.filter(pk__in=[entry.pk for entry in chosen]).delete()
    if deleted != PLAYERS_PER_GAME:
        raise WaitingRoomError("The chosen players are no longer waiting.")
    return game
