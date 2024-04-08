from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ib_core.models import User, TagBinder, TagManager


class TagBinderAdmin(admin.ModelAdmin):
    list_display = ["id", "key", "tag", "bind_creator", "create_date_time_stamp", "allow_many"]
    readonly_fields = ["key", "tag"]
    list_filter = ["related_manager"]


class TagManagerAdmin(admin.ModelAdmin):
    list_display = ["id", "creator", "create_datetime_stamp"]
    filter_horizontal = ["tags"]


class UUIDModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin for UUIDModel instances

    !!! for inheritance only !!!

    Automatically adds 'creator', 'create_date_time_stamp' and 'tag_manager' fields to 'list_display'

    You can change this behaviour by overriding the following fields to False:
        - display_creator
        - display_create_date_time_stamp
        - display_tag_manager
    """
    list_display = []
    readonly_fields = []    # noqa
    readonly_fields.append("tag_manager")

    display_creator = True
    display_create_date_time_stamp = True
    display_tag_manager = True

    def __init__(self, model, admin_site):
        if self.display_creator:
            self.list_display.append("creator")
        if self.display_create_date_time_stamp:
            self.list_display.append("create_date_time_stamp")
        if self.display_tag_manager:
            self.list_display.append("view_tags_manager")
        super().__init__(model, admin_site)

    def view_tags_manager(self, obj):
        return str(obj.tag_manager)

    view_tags_manager.short_description = "Менеджер тегов"


admin.site.register(User, UserAdmin)
admin.site.register(TagBinder, TagBinderAdmin)
admin.site.register(TagManager, TagManagerAdmin)
