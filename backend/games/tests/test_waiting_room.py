from django.test import TestCase

from games.models import Game, GamePlayer, WaitingRoomEntry
from games.waiting_room import form_game

from .factories import create_game, create_user


class FormGameTests(TestCase):
    def test_five_waiting_users_form_one_game_and_two_remain(self):
        old_game = create_game(create_user("veteran"), player_count=1)
        old_game.status = Game.FINISHED
        old_game.save()
        waiting = [old_game.created_by] + [create_user(f"waiting{index}") for index in range(1, 5)]
        for user in waiting:
            WaitingRoomEntry.objects.create(user=user)

        game = form_game()

        self.assertIsNotNone(game)
        game.refresh_from_db()
        self.assertEqual(game.status, Game.WAITING)
        self.assertEqual(Game.objects.count(), 2)
        self.assertEqual(Game.objects.get(pk=old_game.pk).status, Game.FINISHED)
        self.assertEqual(old_game.players.count(), 1)

        players = list(game.players.all())
        chosen = {player.user_id for player in players}
        self.assertEqual(len(players), 3)
        self.assertEqual(len(chosen), 3)
        self.assertTrue(chosen <= {user.id for user in waiting})
        self.assertEqual(sorted(player.player_order for player in players), [1, 2, 3])
        self.assertEqual(len({player.color for player in players}), 3)
        valid_colors = {value for value, _ in GamePlayer.COLOR_CHOICES}
        for player in players:
            self.assertIn(player.color, valid_colors)
            self.assertEqual(player.score, 0)
            self.assertTrue(player.is_active)
        self.assertIn(game.created_by_id, chosen)
        self.assertFalse(game.rounds.exists())

        remaining = set(WaitingRoomEntry.objects.values_list("user_id", flat=True))
        self.assertEqual(remaining, {user.id for user in waiting} - chosen)

    def test_two_waiting_users_change_nothing(self):
        users = [create_user("first"), create_user("second")]
        for user in users:
            WaitingRoomEntry.objects.create(user=user)

        self.assertIsNone(form_game())

        self.assertFalse(Game.objects.exists())
        self.assertFalse(GamePlayer.objects.exists())
        self.assertEqual(
            set(WaitingRoomEntry.objects.values_list("user_id", flat=True)),
            {user.id for user in users},
        )
