# coding: utf-8
from django.apps import AppConfig


class SiteConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "sites_extra"
    verbose_name = "Sites Extra"
