from django.contrib import admin
from django.contrib.auth.models import Group

from apps.users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "username", "phone"]
    list_display_links = ["id", "first_name"]
    list_filter = ["district"]


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
