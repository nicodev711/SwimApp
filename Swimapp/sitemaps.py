from django.contrib.sitemaps import Sitemap
from .models import *


class SwimmingSpotSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return SwimmingSpot.objects.all()

    def lastmod(self, obj):
        return obj.updated
