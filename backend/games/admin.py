from django.contrib import admin

from .models import Game, GamePlayer, Round, RoundAnswer


class GamePlayerInline(admin.TabularInline):
    model = GamePlayer
    extra = 0
    autocomplete_fields = ("user",)


class RoundInline(admin.TabularInline):
    model = Round
    extra = 0
    fields = ("number", "status", "question_type", "choice_question", "numeric_question", "started_at", "finished_at")
    show_change_link = True


class RoundAnswerInline(admin.TabularInline):
    model = RoundAnswer
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "status", "created_at", "started_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("created_by__username",)
    list_select_related = ("created_by",)
    autocomplete_fields = ("created_by",)
    inlines = [GamePlayerInline, RoundInline]


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "player_order", "score", "is_active", "joined_at")
    list_filter = ("is_active", "game__status")
    search_fields = ("user__username",)
    list_select_related = ("user", "game")
    autocomplete_fields = ("user",)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("game", "number", "status", "question_type", "started_at", "finished_at")
    list_filter = ("status", "question_type")
    list_select_related = ("game",)
    inlines = [RoundAnswerInline]


@admin.register(RoundAnswer)
class RoundAnswerAdmin(admin.ModelAdmin):
    list_display = ("round", "player", "selected_option", "numeric_value", "is_correct", "points_awarded", "submitted_at")
    list_filter = ("is_correct", "round__question_type")
    list_select_related = ("round", "player__user", "selected_option")
