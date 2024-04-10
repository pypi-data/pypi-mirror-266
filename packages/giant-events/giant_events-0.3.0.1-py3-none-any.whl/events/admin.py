from django.contrib import admin
from django.conf import settings

from .models import Event, Tag, Location


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin config for EventTag model
    """

    list_display = ["name"]

    fields = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin config for Event model
    """

    list_display = ["title", "start_at", "end_at", "is_published"]
    search_fields = ["title", "location__name"]
    readonly_fields = ["created_at", "updated_at"]
    list_filter = ["is_published"]
    prepopulated_fields = {"slug": ["title"]}

    fieldsets = [
        (
            "Details",
            {
                "fields": [
                    "title",
                    "slug",
                    "intro",
                    "start_at",
                    "end_at",
                    "address",
                    "location",
                    "tags",
                ]
            },
        ),
        ("Image", {"fields": ["photo", "hero_image"]}),
        ("Publishing", {"fields": ["is_published", "publish_at"]}),
        (
            "Metadata",
            {"classes": ("collapse",), "fields": ["created_at", "updated_at"]},
        ),
    ]

    def get_list_display(self, request):
        if hasattr(settings, "EVENT_ADMIN_LIST_DISPLAY"):
            return settings.EVENT_ADMIN_LIST_DISPLAY
        return super().get_list_display(request)

    def get_fieldsets(self, request, obj=None):
        if hasattr(settings, "EVENT_ADMIN_FIELDSETS"):
            return settings.EVENT_ADMIN_FIELDSETS
        return super().get_fieldsets(request, obj)

    def get_search_fields(self, request):
        if hasattr(settings, "EVENT_ADMIN_SEARCH_FIELDS"):
            return settings.EVENT_ADMIN_SEARCH_FIELDS
        return super().get_search_fields(request)

    def get_readonly_fields(self, request, obj=None):
        if hasattr(settings, "EVENT_ADMIN_READONLY_FIELDS"):
            return settings.EVENT_ADMIN_READONLY_FIELDS
        return super().get_readonly_fields(request, obj)

    def get_list_filter(self, request):
        if hasattr(settings, "EVENT_ADMIN_FILTER_FIELDS"):
            return settings.EVENT_ADMIN_FILTER_FIELDS
        return super().get_list_filter(request)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """
    Admin class for the location model
    """

    list_display = ["name", "lat", "lng"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["name", "lat", "lng"]}),
        (
            "Meta Data",
            {"classes": ("collapse",), "fields": ["created_at", "updated_at"]},
        ),
    ]
