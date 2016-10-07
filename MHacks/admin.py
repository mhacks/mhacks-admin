from django.contrib import admin

from models import *


@admin.register(MHacksUser)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ['name', 'info']
    list_display = ['name', 'start', 'duration', 'category']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    search_fields = ['title', 'info']
    list_display = ['title', 'broadcast_at', 'category', 'approved']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'decision']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'acceptance', 'dietary_restrictions',
                     'transportation']


@admin.register(ScanEvent)
class ScanEventAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(ScanEventUser)
class ScanEventUserAdmin(admin.ModelAdmin):
    search_fields = ['scan_event__name']


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    search_fields = ['name']
