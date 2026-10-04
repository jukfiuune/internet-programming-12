from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


def create_choice_question(category, correct_flags=(True, False, False, False)):
    question = ChoiceQuestion.objects.create(category=category, text="Коя е столицата на България?")
    for index, is_correct in enumerate(correct_flags):
        AnswerOption.objects.create(question=question, text=f"Отговор {index + 1}", is_correct=is_correct)
    return question


class CategoryTests(TestCase):
    def test_create_category_with_unique_name(self):
        category = Category(name="География")
        category.full_clean()
        category.save()

        duplicate = Category(name="География")
        with self.assertRaises(ValidationError) as ctx:
            duplicate.full_clean()
        self.assertIn("name", ctx.exception.message_dict)

    def test_category_with_questions_cannot_be_deleted(self):
        category = Category.objects.create(name="История")
        NumericQuestion.objects.create(category=category, text="През коя година?", correct_answer=1878)

        with self.assertRaises(ProtectedError):
            category.delete()
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())


class ChoiceQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="География")

    def test_create_valid_choice_question(self):
        question = create_choice_question(self.category)

        question.full_clean()
        self.assertEqual(question.category, self.category)
        self.assertEqual(self.category.choicequestions.get(), question)
        self.assertEqual(question.answer_options.count(), 4)
        self.assertEqual(question.answer_options.filter(is_correct=True).count(), 1)

    def test_invalid_choice_questions(self):
        cases = {
            "three options": (True, False, False),
            "five options": (True, False, False, False, False),
            "no correct option": (False, False, False, False),
            "two correct options": (True, True, False, False),
        }
        for name, flags in cases.items():
            with self.subTest(name):
                question = create_choice_question(self.category, flags)
                with self.assertRaises(ValidationError):
                    question.full_clean()

    def test_deleting_question_deletes_answer_options(self):
        question = create_choice_question(self.category)

        question.delete()

        self.assertFalse(AnswerOption.objects.exists())


class NumericQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Наука")

    def test_create_numeric_question(self):
        question = NumericQuestion(category=self.category, text="Колко са планетите?", correct_answer=8)
        question.full_clean()
        question.save()

        self.assertEqual(self.category.numericquestions.get().correct_answer, 8)

    def test_correct_answer_is_required_integer(self):
        for value in (None, "осем"):
            with self.subTest(value=value):
                question = NumericQuestion(category=self.category, text="Колко?", correct_answer=value)
                with self.assertRaises(ValidationError) as ctx:
                    question.full_clean()
                self.assertIn("correct_answer", ctx.exception.message_dict)
