from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from games.models import Game, GamePlayer, Round, RoundAnswer

from .factories import (
    create_choice_question,
    create_choice_round,
    create_game,
    create_numeric_round,
    create_user,
)


class GameTests(TestCase):
    def test_new_game_defaults(self):
        creator = create_user("host")
        game = Game.objects.create(created_by=creator)

        self.assertEqual(game.status, Game.WAITING)
        self.assertIsNotNone(game.created_at)
        self.assertIsNone(game.started_at)
        self.assertIsNone(game.finished_at)
        self.assertEqual(list(creator.created_games.all()), [game])

    def test_invalid_status_is_rejected(self):
        game = Game(created_by=create_user("host"), status="paused")

        with self.assertRaises(ValidationError) as ctx:
            game.full_clean()
        self.assertIn("status", ctx.exception.message_dict)

    def test_game_lifecycle_timestamps(self):
        game = create_game()
        game.status = Game.IN_PROGRESS
        game.started_at = timezone.now()
        game.full_clean()
        game.save()

        game.status = Game.FINISHED
        game.finished_at = game.started_at - timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            game.full_clean()

        game.finished_at = game.started_at + timezone.timedelta(minutes=5)
        game.full_clean()

    def test_deleting_game_deletes_players_rounds_and_answers(self):
        game = create_game()
        round_ = create_numeric_round(game)
        RoundAnswer.objects.create(round=round_, player=game.players.first(), numeric_value=5)

        game.delete()

        self.assertFalse(GamePlayer.objects.exists())
        self.assertFalse(Round.objects.exists())
        self.assertFalse(RoundAnswer.objects.exists())

    def test_user_in_a_game_cannot_be_deleted(self):
        game = create_game()

        for user in (game.created_by, game.players.last().user):
            with self.subTest(user=user.username), self.assertRaises(ProtectedError):
                user.delete()


class GamePlayerTests(TestCase):
    def test_players_defaults_and_order(self):
        game = create_game(player_count=3)

        players = list(game.players.all())
        self.assertEqual([player.player_order for player in players], [1, 2, 3])
        self.assertEqual(players[0].user, game.created_by)
        for player in players:
            self.assertEqual(player.score, 0)
            self.assertTrue(player.is_active)
            self.assertIsNotNone(player.joined_at)

    def test_user_can_join_many_games(self):
        user = create_user("host")
        first = create_game(creator=user, player_count=1)
        second = Game.objects.create(created_by=create_user("other"))
        GamePlayer.objects.create(game=second, user=user, player_order=1)

        self.assertEqual({player.game for player in user.game_players.all()}, {first, second})


class RoundTests(TestCase):
    def setUp(self):
        self.game = create_game()

    def test_rounds_are_ordered_and_use_one_question(self):
        numeric = create_numeric_round(self.game, number=2)
        choice = create_choice_round(self.game, number=1)

        self.assertEqual(list(self.game.rounds.all()), [choice, numeric])
        self.assertEqual(choice.status, Round.PENDING)
        self.assertEqual(choice.question, choice.choice_question)
        self.assertEqual(numeric.question, numeric.numeric_question)
        self.assertEqual(list(choice.choice_question.rounds.all()), [choice])

    def test_round_lifecycle(self):
        round_ = create_choice_round(self.game)

        for status in (Round.OPEN, Round.CLOSED, Round.EVALUATED):
            round_.status = status
            round_.full_clean()
            round_.save()

        round_.refresh_from_db()
        self.assertEqual(round_.status, Round.EVALUATED)

    def test_round_question_must_match_type(self):
        choice_question = create_choice_question()
        cases = {
            "choice without question": Round(game=self.game, number=1, question_type=Round.CHOICE),
            "choice with numeric question": Round(
                game=self.game,
                number=1,
                question_type=Round.NUMERIC,
                choice_question=choice_question,
            ),
            "both questions": Round(
                game=self.game,
                number=1,
                question_type=Round.CHOICE,
                choice_question=choice_question,
                numeric_question=create_numeric_round(create_game(create_user("x"), 1)).numeric_question,
            ),
        }
        for name, round_ in cases.items():
            with self.subTest(name), self.assertRaises(ValidationError):
                round_.full_clean()

    def test_question_used_in_round_cannot_be_deleted(self):
        round_ = create_choice_round(self.game)

        with self.assertRaises(ProtectedError):
            round_.choice_question.delete()


class RoundAnswerTests(TestCase):
    def setUp(self):
        self.game = create_game()
        self.player = self.game.players.first()
        self.choice_round = create_choice_round(self.game, number=1)
        self.numeric_round = create_numeric_round(self.game, number=2)

    def test_create_answers(self):
        option = self.choice_round.choice_question.answer_options.get(is_correct=True)
        choice_answer = RoundAnswer(round=self.choice_round, player=self.player, selected_option=option, submitted_at=timezone.now())
        numeric_answer = RoundAnswer(round=self.numeric_round, player=self.player, numeric_value=5)
        for answer in (choice_answer, numeric_answer):
            answer.full_clean()
            answer.save()

        self.assertIsNone(numeric_answer.is_correct)
        self.assertEqual(numeric_answer.points_awarded, 0)
        self.assertEqual(list(self.player.answers.all()), [choice_answer, numeric_answer])
        self.assertEqual(list(self.choice_round.answers.all()), [choice_answer])

    def test_answer_must_match_round(self):
        outsider = create_game(create_user("outsider"), 1).players.get()
        other_question_option = create_choice_question("Друг въпрос?").answer_options.first()
        own_option = self.choice_round.choice_question.answer_options.first()
        cases = {
            ("player", "player from another game"): RoundAnswer(round=self.numeric_round, player=outsider, numeric_value=1),
            ("selected_option", "option from another question"): RoundAnswer(
                round=self.choice_round, player=self.player, selected_option=other_question_option
            ),
            ("numeric_value", "number in choice round"): RoundAnswer(round=self.choice_round, player=self.player, numeric_value=3),
            ("selected_option", "option in numeric round"): RoundAnswer(
                round=self.numeric_round, player=self.player, selected_option=own_option
            ),
        }
        for (field, name), answer in cases.items():
            with self.subTest(name), self.assertRaises(ValidationError) as ctx:
                answer.full_clean()
            self.assertIn(field, ctx.exception.message_dict)

    def test_option_used_in_answer_cannot_be_deleted(self):
        option = self.choice_round.choice_question.answer_options.first()
        RoundAnswer.objects.create(round=self.choice_round, player=self.player, selected_option=option)

        with self.assertRaises(ProtectedError):
            option.delete()
