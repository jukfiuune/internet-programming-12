from django.core.exceptions import ValidationError
from django.db import models

ANSWER_OPTIONS_COUNT = 4


def validate_answer_options(correct_flags):
    errors = []
    if len(correct_flags) != ANSWER_OPTIONS_COUNT:
        errors.append(f"A choice question must have exactly {ANSWER_OPTIONS_COUNT} answer options.")
    if sum(bool(flag) for flag in correct_flags) != 1:
        errors.append("A choice question must have exactly one correct answer option.")
    if errors:
        raise ValidationError(errors)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class BaseQuestion(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    text = models.TextField()

    class Meta:
        abstract = True
        ordering = ["id"]

    def __str__(self):
        return self.text


class ChoiceQuestion(BaseQuestion):
    def clean(self):
        super().clean()
        if self.pk is not None:
            validate_answer_options(list(self.answer_options.values_list("is_correct", flat=True)))


class NumericQuestion(BaseQuestion):
    correct_answer = models.IntegerField()


class AnswerOption(models.Model):
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="answer_options",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.text
