from django.contrib import admin
from .models import Room, Reading


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('room', 'timestamp', 'temp_c', 'temp_f', 'bpm')
    list_filter = ('room',)
    ordering = ('-timestamp',)

from .models import Monitor


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'room')
    list_editable = ('room',)
