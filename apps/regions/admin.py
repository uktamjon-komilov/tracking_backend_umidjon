from django.contrib import admin

from apps.regions.models import Region, District


class DistrictAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "region"]
    list_display_links = ["id", "name"]
    list_filter = ["region"]
    search_fields = ["name"]


admin.site.register(Region)
admin.site.register(District, DistrictAdmin)
