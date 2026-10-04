from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class QuestionBankFixtureTests(TestCase):
    fixtures = ["questions/question_bank.json"]

    def test_fixture_counts(self):
        self.assertEqual(Category.objects.count(), 6)
        self.assertEqual(ChoiceQuestion.objects.count(), 12)
        self.assertEqual(AnswerOption.objects.count(), 48)
        self.assertEqual(NumericQuestion.objects.count(), 12)

    def test_choice_questions_are_valid(self):
        for question in ChoiceQuestion.objects.prefetch_related("answer_options"):
            with self.subTest(question=question.pk):
                options = list(question.answer_options.all())
                self.assertEqual(len(options), 4)
                self.assertEqual(sum(option.is_correct for option in options), 1)
                question.full_clean()

    def test_numeric_questions_have_integer_answers(self):
        for question in NumericQuestion.objects.all():
            with self.subTest(question=question.pk):
                self.assertIsInstance(question.correct_answer, int)
                question.full_clean()
