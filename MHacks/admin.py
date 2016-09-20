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
    search_fields = ['name', 'info', 'location']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    search_fields = ['title', 'info']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'decision']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'decision']


@admin.register(ScanEvent)
class ScanEventAdmin(admin.ModelAdmin):
    search_fields = ['name']
