from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import ANSWER_OPTIONS_COUNT, AnswerOption, Category, ChoiceQuestion, NumericQuestion, validate_answer_options


class AnswerOptionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        flags = [
            form.cleaned_data.get("is_correct", False)
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE")
        ]
        try:
            validate_answer_options(flags)
        except ValidationError as exc:
            raise ValidationError(exc.messages)


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionFormSet
    min_num = ANSWER_OPTIONS_COUNT
    max_num = ANSWER_OPTIONS_COUNT
    validate_min = True
    validate_max = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category")
    list_filter = ("category",)
    search_fields = ("text",)
    list_select_related = ("category",)
    inlines = [AnswerOptionInline]


@admin.register(NumericQuestion)
class NumericQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "correct_answer")
    list_filter = ("category",)
    search_fields = ("text",)
    list_select_related = ("category",)
