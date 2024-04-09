from cms.models import PlaceholderField
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from filer.fields.image import FilerImageField
from mixins.models import (
    PublishingMixin,
    PublishingQuerySetMixin,
    TimestampMixin,
    URLMixin,
)


class Tag(TimestampMixin):
    """
    Model to store a tag for the Event model
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        """
        String representation of a Tag object, in the Events app
        """
        return self.name


class Location(TimestampMixin):
    """
    Location that is tied to an event
    """

    name = models.CharField(max_length=255, unique=True)
    lng = models.DecimalField(max_digits=12, decimal_places=10)
    lat = models.DecimalField(max_digits=12, decimal_places=10)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["name"]

    def __str__(self):
        """
        String representation of the location object, in the Events app
        """
        return self.name


class EventQuerySet(PublishingQuerySetMixin):
    """
    Custom QuerySet model to override the base one
    """

    def future(self, user=None):
        """
        Return the published queryset for future events. Filter on start_date OR end_date being in
        the future as some events don't have end dates.
        """
        now = timezone.now()
        return self.published(user=user).filter(
            Q(start_at__gte=now) | Q(end_at__gte=now)
        )

    def past(self, user=None):
        """
        Return the published queryset for past events.
        """
        return self.published(user=user).filter(end_at__lt=timezone.now())


class Event(TimestampMixin, PublishingMixin, URLMixin):
    """
    Model for creating and storing and event object
    """

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    photo = FilerImageField(
        related_name="%(app_label)s_%(class)s_images",
        on_delete=models.SET_NULL,
        null=True,
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(blank=True, null=True)
    intro = models.CharField(max_length=255)
    content = PlaceholderField(slotname="event_content", related_name="event_content")
    hero_image = FilerImageField(
        related_name="+",
        help_text="Select an image that will be displayed as the hero for the event detail page. ",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name="Tags",
        related_name="%(app_label)s_%(class)s_tags",
        blank=True,
    )
    address = models.CharField(max_length=255, blank=True)
    location = models.ForeignKey(
        to=Location, null=True, on_delete=models.SET_NULL, related_name="events"
    )
    cta_text = models.CharField(max_length=255, blank=True)

    objects = EventQuerySet.as_manager()

    class Meta:
        # We need both orders to make sure that hours are respected. Purely using the start_at
        # would not correctly sort 2 items with the same date but different hours.
        ordering = ["start_at__date", "start_at__time"]
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        """
        Returns the string representation of the event object
        """
        return self.title

    def get_absolute_url(self):
        """
        Builds the url for the event object
        """
        return reverse("events:detail", kwargs={"slug": self.slug})
