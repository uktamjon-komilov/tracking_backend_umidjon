from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import TextInput

from apps.regions.models import Region, District


class DistrictForm(ModelForm):
    class Meta:
        model = District
        fields = "__all__"
        widgets = {
            "user_color": TextInput(
                attrs={
                    "type": "color",
                }
            ),
        }


class DistrictAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "region"]
    list_display_links = ["id", "name"]
    list_filter = ["region"]
    search_fields = ["name"]
    form = DistrictForm


admin.site.register(Region)
admin.site.register(District, DistrictAdmin)
