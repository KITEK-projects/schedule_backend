from django.contrib import admin
from app.admin import admin_site
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from my_auth.models import Group, MyUser


class MyUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "first_name", "last_name", "password1", "password2", "role"),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "curator")
    filter_horizontal = ("students",)


admin_site.register(MyUser, MyUserAdmin)
admin_site.register(Group, GroupAdmin)
