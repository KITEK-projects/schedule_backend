from django.contrib import admin
from app.admin import admin_site
from rustore.models import RustoreVersion

class RustoreVersionAdmin(admin.ModelAdmin):
    list_display = ("versionName", "versionCode")
    search_fields = ("versionName", "versionCode")
    ordering = ("-versionCode",)


admin_site.register(RustoreVersion, RustoreVersionAdmin)