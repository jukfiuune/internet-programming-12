from django.contrib.auth import get_user_model

from games.models import Game, GamePlayer, Round
from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion

User = get_user_model()


def create_user(username):
    return User.objects.create_user(username=username, email=f"{username}@example.com", password="pw-12345678")


def create_category(name="География"):
    return Category.objects.get_or_create(name=name)[0]


def create_choice_question(text="Коя е столицата на България?"):
    question = ChoiceQuestion.objects.create(category=create_category(), text=text)
    for index, answer in enumerate(["София", "Пловдив", "Варна", "Бургас"]):
        AnswerOption.objects.create(question=question, text=answer, is_correct=index == 0)
    return question


def create_numeric_question(text="С колко държави граничи България?", correct_answer=5):
    return NumericQuestion.objects.create(category=create_category(), text=text, correct_answer=correct_answer)


def create_game(creator=None, player_count=2):
    creator = creator or create_user("host")
    game = Game.objects.create(created_by=creator)
    users = [creator] + [create_user(f"player{index}") for index in range(1, player_count)]
    for order, user in enumerate(users, start=1):
        GamePlayer.objects.create(game=game, user=user, player_order=order)
    return game


def create_choice_round(game, number=1, question=None):
    return Round.objects.create(
        game=game,
        number=number,
        question_type=Round.CHOICE,
        choice_question=question or create_choice_question(),
    )


def create_numeric_round(game, number=1, question=None):
    return Round.objects.create(
        game=game,
        number=number,
        question_type=Round.NUMERIC,
        numeric_question=question or create_numeric_question(),
    )
