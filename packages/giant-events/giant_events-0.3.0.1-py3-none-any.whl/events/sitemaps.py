from django.contrib.sitemaps import Sitemap

from .models import Event


class EventSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        """
        Get all active events
        """
        return Event.objects.published()

    def lastmod(self, obj):
        return obj.updated_at
