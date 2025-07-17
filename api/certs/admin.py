from django.contrib import admin
from app.admin import admin_site
from certs.models import Cert


class CertAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "first_name",
        "last_name",
        "group",
        "requested_by",
        "quantity",
    )
    search_fields = ("first_name", "last_name", "requested_by", "group")
    list_filter = ("status", "group")

    actions = ["mark_as_ready"]

    @admin.action(description="Пометить как готовое")
    def mark_as_ready(self, request, queryset):
        updated_count = queryset.update(status=Cert.STATUS.READY)
        self.message_user(request, f"{updated_count} записей помечено как готовое")


admin_site.register(Cert, CertAdmin)
