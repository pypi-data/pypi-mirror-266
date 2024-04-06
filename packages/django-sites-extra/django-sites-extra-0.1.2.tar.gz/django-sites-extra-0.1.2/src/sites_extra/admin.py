from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from .models import Background


@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ["name"]
    ordering = ("name",)
    search_fields = ["name"]


class ProxySite(Site):
    """Create Association proxy model for Site Django framework"""

    class Meta:
        proxy = True
        verbose_name = Site._meta.verbose_name
        verbose_name_plural = Site._meta.verbose_name_plural


admin.site.unregister(Site)
admin.site.register(ProxySite, SiteAdmin)
