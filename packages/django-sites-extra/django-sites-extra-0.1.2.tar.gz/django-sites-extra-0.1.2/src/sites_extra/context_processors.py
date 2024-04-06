"""
Context processors for site app
"""

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache


def info(request):
    """
    Return a SITE_URL and SITE_TITLE template context for the current request.
    """

    cache_key = "site_info_context"
    context_cache = None
    try:
        context_cache = cache.get(cache_key)
    except Exception as err:
        context_cache = None

    if context_cache is None:
        try:
            if request.is_secure():
                scheme = "https://"
            else:
                scheme = "http://"
            current_site = get_current_site(request)
            context = {
                "SITE_URL": scheme + request.get_host(),
                # 'SITE_URL': scheme + current_site.domain,
                "SITE_TITLE": current_site.name,
            }
            context_cache = cache.set(cache_key, context, timeout=86400)
            return context
        except Exception as err:
            messages.error(request, err)
    return context_cache
