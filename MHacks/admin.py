from django.contrib import admin

from announcements import AnnouncementModel
from events import EventModel
from locations import LocationModel
from floors import FloorModel
from scan_events import ScanEventModel, ScanEventUser
from users import MHacksUser


@admin.register(MHacksUser)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(LocationModel)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(EventModel)
class EventAdmin(admin.ModelAdmin):
    search_fields = ['name', 'info']
    list_display = ['name', 'start', 'duration', 'category', 'deleted_string', 'location_list']

    def deleted_string(self, obj):
        return 'Deleted' if obj.deleted else ''

    def location_list(self, obj):
        print(obj.locations.all())
        return ', '.join(map(lambda l: l.__unicode__(), obj.locations.all()))

    deleted_string.short_description = 'DELETED'
    location_list.short_description = 'LOCATIONS'


@admin.register(AnnouncementModel)
class AnnouncementAdmin(admin.ModelAdmin):
    search_fields = ['title', 'info']
    list_display = ['title', 'broadcast_at', 'category', 'sent', 'approved', 'deleted_string']

    def deleted_string(self, obj):
        return 'Deleted' if obj.deleted else ''

    deleted_string.short_description = 'DELETED'


@admin.register(ScanEventModel)
class ScanEventAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(ScanEventUser)
class ScanEventUserAdmin(admin.ModelAdmin):
    search_fields = ['scan_event__name']


@admin.register(FloorModel)
class FloorAdmin(admin.ModelAdmin):
    search_fields = ['name']
