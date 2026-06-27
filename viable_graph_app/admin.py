from django.contrib import admin
from .models import Problem, Suggestion, Comment, CommentRating


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "is_approved",
        "reported_by",
        "created_at",
    )
    list_filter = ("category", "status", "is_approved", "created_at")
    search_fields = ("title", "description")
    list_editable = ("status", "is_approved")
    actions = ["approve_problems", "reject_problems"]

    @admin.action(description="✅ อนุมัติปัญหาที่เลือก")
    def approve_problems(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="❌ ไม่อนุมัติปัญหาที่เลือก")
    def reject_problems(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("problem", "votes", "created_at")
    search_fields = ("suggestion_text",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "problem",
        "text",
        "rating_average",
        "rating_count",
        "is_reported",
        "created_at",
    )
    list_filter = ("is_reported", "created_at")
    search_fields = ("text", "author__username")
    list_editable = ("is_reported",)


@admin.register(CommentRating)
class CommentRatingAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "comment__text")
