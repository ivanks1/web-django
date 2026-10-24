from django.contrib import admin

from .models import Resume, UserProfiles


@admin.register(UserProfiles)
class UserProfilesAdmin(admin.ModelAdmin):
    list_display = ("username", "display_name", "age", "city", "email")
    search_fields = ("username", "display_name", "city", "email")
    list_filter = ("city",)


@admin.register(Resume)

class ResumeAdmin(admin.ModelAdmin):
    list_display = ("surname", "name", "age", "profession", "created_at")
    search_fields = ("surname", "name", "profession", "skills")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

