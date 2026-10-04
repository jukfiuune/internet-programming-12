from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from games.models import Game, GamePlayer, Round, RoundAnswer

from .factories import create_choice_question, create_game, create_numeric_question, create_numeric_round, create_user


class ConstraintTestCase(TestCase):
    def assertIntegrityError(self, create):
        with self.assertRaises(IntegrityError), transaction.atomic():
            create()


class GameConstraintTests(ConstraintTestCase):
    def test_game_cannot_finish_before_start(self):
        now = timezone.now()
        creator = create_user("host")

        self.assertIntegrityError(lambda: Game.objects.create(created_by=creator, finished_at=now))
        self.assertIntegrityError(
            lambda: Game.objects.create(created_by=creator, started_at=now, finished_at=now - timezone.timedelta(seconds=1))
        )


class GamePlayerConstraintTests(ConstraintTestCase):
    def setUp(self):
        self.game = create_game(player_count=2)

    def test_user_joins_game_once(self):
        self.assertIntegrityError(
            lambda: GamePlayer.objects.create(game=self.game, user=self.game.created_by, player_order=3)
        )

    def test_player_order_is_unique_per_game(self):
        self.assertIntegrityError(
            lambda: GamePlayer.objects.create(game=self.game, user=create_user("late"), player_order=1)
        )

    def test_same_order_allowed_in_other_game(self):
        other = create_game(create_user("other_host"), player_count=1)

        self.assertEqual(other.players.get().player_order, 1)

    def test_unique_constraints_are_reported_by_full_clean(self):
        player = GamePlayer(game=self.game, user=self.game.created_by, player_order=2)

        with self.assertRaises(ValidationError):
            player.full_clean()


class RoundConstraintTests(ConstraintTestCase):
    def setUp(self):
        self.game = create_game()

    def test_round_number_is_unique_per_game(self):
        create_numeric_round(self.game, number=1)

        self.assertIntegrityError(lambda: create_numeric_round(self.game, number=1))

    def test_round_requires_exactly_one_matching_question(self):
        choice = create_choice_question()
        numeric = create_numeric_question()
        cases = {
            "no question": {"question_type": Round.CHOICE},
            "choice type with numeric question": {"question_type": Round.CHOICE, "numeric_question": numeric},
            "numeric type with choice question": {"question_type": Round.NUMERIC, "choice_question": choice},
            "both questions": {"question_type": Round.CHOICE, "choice_question": choice, "numeric_question": numeric},
        }
        for number, (name, fields) in enumerate(cases.items(), start=1):
            with self.subTest(name):
                self.assertIntegrityError(lambda: Round.objects.create(game=self.game, number=number, **fields))


class RoundAnswerConstraintTests(ConstraintTestCase):
    def setUp(self):
        self.game = create_game()
        self.player = self.game.players.first()
        self.round = create_numeric_round(self.game)

    def test_one_answer_per_player_per_round(self):
        RoundAnswer.objects.create(round=self.round, player=self.player, numeric_value=4)

        self.assertIntegrityError(lambda: RoundAnswer.objects.create(round=self.round, player=self.player, numeric_value=5))

    def test_answer_cannot_have_option_and_number(self):
        option = create_choice_question().answer_options.first()

        self.assertIntegrityError(
            lambda: RoundAnswer.objects.create(round=self.round, player=self.player, selected_option=option, numeric_value=5)
        )
