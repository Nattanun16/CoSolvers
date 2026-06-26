from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Problem, Suggestion, Comment, CommentRating


class PendingEditFilter(admin.SimpleListFilter):
    """Filter พิเศษสำหรับกรองปัญหาที่มีการแก้ไขรออนุมัติ"""
    title = "สถานะการแก้ไข"
    parameter_name = "pending_edit_status"

    def lookups(self, request, model_admin):
        return [
            ("pending", "⚠️ รออนุมัติการแก้ไข"),
            ("no_pending", "✅ ไม่มีการแก้ไขค้างอยู่"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "pending":
            return queryset.filter(has_pending_edit=True)
        if self.value() == "no_pending":
            return queryset.filter(has_pending_edit=False)
        return queryset


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "title_with_pending_badge",
        "category",
        "status",
        "is_approved",
        "pending_edit_info",
        "reported_by",
        "created_at",
        "quick_actions",
    )
    list_filter = ("category", "status", "is_approved", PendingEditFilter, "created_at")
    search_fields = ("title", "description", "pending_title")
    list_editable = (
        "status",
        "is_approved",
    )
    actions = ["approve_problems", "reject_problems", "approve_pending_edits", "reject_pending_edits"]
    readonly_fields = ("pending_edit_preview",)

    def get_queryset(self, request):
        """เรียง pending edit ขึ้นก่อน"""
        qs = super().get_queryset(request)
        return qs.order_by("-has_pending_edit", "-created_at")

    def title_with_pending_badge(self, obj):
        """แสดงชื่อปัญหาพร้อม badge สีส้มถ้ามี pending edit"""
        if obj.has_pending_edit:
            return format_html(
                '<span style="color:#b45309; font-weight:bold;">⚠️ {}</span>'
                '<br><small style="color:#92400e;">📝 รออนุมัติการแก้ไข</small>',
                obj.title,
            )
        return obj.title

    title_with_pending_badge.short_description = "ชื่อปัญหา"
    title_with_pending_badge.admin_order_field = "title"

    def pending_edit_info(self, obj):
        """แสดงชื่อใหม่ที่รออนุมัติ"""
        if not obj.has_pending_edit:
            return format_html('<span style="color:#6b7280;">—</span>')
        lines = []
        if obj.pending_title and obj.pending_title != obj.title:
            lines.append(
                f'<b>ชื่อใหม่:</b> <span style="color:#1d4ed8;">{obj.pending_title}</span>'
            )
        if obj.pending_category and obj.pending_category != obj.category:
            cat_display = dict(Problem.CATEGORY_CHOICES).get(obj.pending_category, obj.pending_category)
            lines.append(f'<b>หมวดใหม่:</b> {cat_display}')
        if obj.pending_description and obj.pending_description != obj.description:
            preview = (obj.pending_description or "")[:60]
            lines.append(f'<b>รายละเอียด:</b> {preview}…')
        if not lines:
            lines.append('<span style="color:#6b7280;">มีการแก้ไข (ดูรายละเอียดในหน้า Edit)</span>')
        return format_html('<br>'.join(lines))

    pending_edit_info.short_description = "การแก้ไขที่รออนุมัติ"
    pending_edit_info.allow_tags = True

    def quick_actions(self, obj):
        """ปุ่มอนุมัติ/ปฏิเสธ inline ในแถว"""
        if not obj.has_pending_edit:
            return format_html('<span style="color:#d1d5db;">—</span>')
        approve_url = f"approve-edit/{obj.pk}/"
        reject_url = f"reject-edit/{obj.pk}/"
        return format_html(
            '<a href="{}" style="background:#16a34a;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;font-size:12px;margin-right:4px;">✅ อนุมัติ</a>'
            '<a href="{}" style="background:#dc2626;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;font-size:12px;">❌ ปฏิเสธ</a>',
            approve_url, reject_url,
        )

    quick_actions.short_description = "จัดการการแก้ไข"

    def pending_edit_preview(self, obj):
        """แสดงตารางเปรียบเทียบข้อมูลเดิมกับข้อมูลใหม่ในหน้า detail"""
        if not obj.has_pending_edit:
            return mark_safe('<p style="color:#6b7280;">ไม่มีการแก้ไขรออนุมัติ</p>')

        fields = [
            ("ชื่อปัญหา", obj.title, obj.pending_title),
            ("หมวดหมู่", obj.get_category_display(),
             dict(Problem.CATEGORY_CHOICES).get(obj.pending_category, obj.pending_category) if obj.pending_category else None),
            ("รายละเอียด", (obj.description or "")[:100], (obj.pending_description or "")[:100]),
            ("สถานที่", obj.location, obj.pending_location),
            ("แท็ก", obj.tags, obj.pending_tags),
            ("วันที่เกิดเหตุ", str(obj.incident_date or ""), str(obj.pending_incident_date or "")),
        ]

        rows = ""
        for label, old_val, new_val in fields:
            if new_val is not None and new_val != old_val:
                rows += (
                    f'<tr>'
                    f'<td style="padding:6px 12px;font-weight:bold;border:1px solid #e5e7eb;">{label}</td>'
                    f'<td style="padding:6px 12px;background:#fef2f2;border:1px solid #e5e7eb;">{old_val}</td>'
                    f'<td style="padding:6px 12px;background:#f0fdf4;border:1px solid #e5e7eb;font-weight:bold;">{new_val}</td>'
                    f'</tr>'
                )

        if obj.pending_photo:
            rows += (
                f'<tr>'
                f'<td style="padding:6px 12px;font-weight:bold;border:1px solid #e5e7eb;">รูปภาพ</td>'
                f'<td style="padding:6px 12px;background:#fef2f2;border:1px solid #e5e7eb;">(รูปเดิม)</td>'
                f'<td style="padding:6px 12px;background:#f0fdf4;border:1px solid #e5e7eb;">'
                f'<img src="{obj.pending_photo.url}" style="max-height:120px;max-width:200px;">'
                f'</td>'
                f'</tr>'
            )

        if not rows:
            rows = '<tr><td colspan="3" style="padding:6px 12px;color:#6b7280;">ไม่พบความแตกต่าง</td></tr>'

        return mark_safe(
            f'<div style="background:#fffbeb;border:2px solid #f59e0b;padding:12px;border-radius:6px;margin-bottom:12px;">'
            f'<b style="color:#b45309;">⚠️ มีการแก้ไขรออนุมัติ</b><br><br>'
            f'<table style="border-collapse:collapse;width:100%;">'
            f'<thead><tr>'
            f'<th style="padding:6px 12px;background:#f3f4f6;border:1px solid #e5e7eb;">ฟิลด์</th>'
            f'<th style="padding:6px 12px;background:#fef2f2;border:1px solid #e5e7eb;">ข้อมูลเดิม</th>'
            f'<th style="padding:6px 12px;background:#f0fdf4;border:1px solid #e5e7eb;">ข้อมูลใหม่ (รออนุมัติ)</th>'
            f'</tr></thead>'
            f'<tbody>{rows}</tbody>'
            f'</table>'
            f'</div>'
        )

    pending_edit_preview.short_description = "เปรียบเทียบการแก้ไข"

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj and obj.has_pending_edit and "pending_edit_preview" not in fields:
            fields = list(fields)
            fields.insert(0, "pending_edit_preview")
        return fields

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path("approve-edit/<int:problem_id>/", self.admin_site.admin_view(self.approve_edit_view), name="approve_edit"),
            path("reject-edit/<int:problem_id>/", self.admin_site.admin_view(self.reject_edit_view), name="reject_edit"),
        ]
        return custom_urls + urls

    def approve_edit_view(self, request, problem_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        problem = get_object_or_404(Problem, pk=problem_id)
        if problem.has_pending_edit:
            if problem.pending_title:
                problem.title = problem.pending_title
            if problem.pending_category:
                problem.category = problem.pending_category
            if problem.pending_description is not None:
                problem.description = problem.pending_description
            if problem.pending_location is not None:
                problem.location = problem.pending_location
            if problem.pending_tags is not None:
                problem.tags = problem.pending_tags
            if problem.pending_incident_date is not None:
                problem.incident_date = problem.pending_incident_date
            if problem.pending_photo:
                problem.photo = problem.pending_photo
            problem.pending_title = None
            problem.pending_category = None
            problem.pending_description = None
            problem.pending_location = None
            problem.pending_tags = None
            problem.pending_incident_date = None
            problem.pending_photo = None
            problem.has_pending_edit = False
            problem.is_approved = True
            problem.save()
            messages.success(request, f'✅ อนุมัติการแก้ไขปัญหา "{problem.title}" เรียบร้อยแล้ว')
        else:
            messages.warning(request, "ไม่พบการแก้ไขที่รออนุมัติ")
        return redirect("../")

    def reject_edit_view(self, request, problem_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        problem = get_object_or_404(Problem, pk=problem_id)
        if problem.has_pending_edit:
            problem.pending_title = None
            problem.pending_category = None
            problem.pending_description = None
            problem.pending_location = None
            problem.pending_tags = None
            problem.pending_incident_date = None
            problem.pending_photo = None
            problem.has_pending_edit = False
            problem.save()
            messages.success(request, f'❌ ปฏิเสธการแก้ไขปัญหา "{problem.title}" แล้ว ข้อมูลเดิมยังคงอยู่')
        else:
            messages.warning(request, "ไม่พบการแก้ไขที่รออนุมัติ")
        return redirect("../")

    def approve_problems(self, request, queryset):
        queryset.update(is_approved=True)

    approve_problems.short_description = "✅ อนุมัติปัญหาที่เลือก"

    def reject_problems(self, request, queryset):
        queryset.update(is_approved=False)

    reject_problems.short_description = "❌ ไม่อนุมัติปัญหาที่เลือก"

    def approve_pending_edits(self, request, queryset):
        """อนุมัติการแก้ไข: copy pending fields มาแทนของจริง แล้วล้าง pending"""
        count = 0
        for problem in queryset.filter(has_pending_edit=True):
            if problem.pending_title:
                problem.title = problem.pending_title
            if problem.pending_category:
                problem.category = problem.pending_category
            if problem.pending_description is not None:
                problem.description = problem.pending_description
            if problem.pending_location is not None:
                problem.location = problem.pending_location
            if problem.pending_tags is not None:
                problem.tags = problem.pending_tags
            if problem.pending_incident_date is not None:
                problem.incident_date = problem.pending_incident_date
            if problem.pending_photo:
                problem.photo = problem.pending_photo

            # ล้าง pending fields
            problem.pending_title = None
            problem.pending_category = None
            problem.pending_description = None
            problem.pending_location = None
            problem.pending_tags = None
            problem.pending_incident_date = None
            problem.pending_photo = None
            problem.has_pending_edit = False
            problem.is_approved = True
            problem.save()
            count += 1
        self.message_user(request, f"✅ อนุมัติการแก้ไขแล้ว {count} รายการ")

    approve_pending_edits.short_description = "✅ อนุมัติการแก้ไขที่รออยู่ (ใช้ข้อมูลใหม่)"

    def reject_pending_edits(self, request, queryset):
        """ปฏิเสธการแก้ไข: ล้าง pending fields ทิ้ง ของเดิมยังอยู่ครบ"""
        count = 0
        for problem in queryset.filter(has_pending_edit=True):
            problem.pending_title = None
            problem.pending_category = None
            problem.pending_description = None
            problem.pending_location = None
            problem.pending_tags = None
            problem.pending_incident_date = None
            problem.pending_photo = None
            problem.has_pending_edit = False
            problem.save()
            count += 1
        self.message_user(request, f"❌ ปฏิเสธการแก้ไขแล้ว {count} รายการ ข้อมูลเดิมยังคงอยู่")

    reject_pending_edits.short_description = "❌ ปฏิเสธการแก้ไข (คืนเป็นข้อมูลเดิม)"


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